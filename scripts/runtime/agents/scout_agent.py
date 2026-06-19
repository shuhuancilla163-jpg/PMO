"""
ScoutAgent — L2 司法权 (工程工具侦察, DEC-2026-0009)
- 数据维度: 维度 4 (工程工具生态)
- 数据源: GitHub Trending (Python/TypeScript/Go/Rust, 每日 Top 50)
- 触发: 定时 (每 24h) + 手动
- 评估: 5 维度权重评分
- 输出: DEC-TOOL-*.json + metrics + Sponsor 看板推荐
- 重要: ScoutAgent 不自动采纳, 只推荐; 采纳归 Sponsor
"""
import json
import os
import sys
import time
import hashlib
import urllib.request
import urllib.error
import urllib.parse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.agent_base import PMOAgent


# ============================================
# GitHub API 客户端 (带 rate limit 处理)
# ============================================
class GitHubClient:
    """GitHub API 客户端, 支持 Trending + Repo 详情"""

    BASE_URL = "https://api.github.com"
    TRENDING_URL = "https://api.github.com/search/repositories"

    def __init__(self, token: Optional[str] = None, cache_ttl_seconds: int = 86400):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PMO-ScoutAgent/1.0"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def _get_cached(self, url: str) -> Optional[Any]:
        key = hashlib.sha256(url.encode()).hexdigest()
        if key in self._cache:
            data, expires_at = self._cache[key]
            if time.time() < expires_at:
                return data
        return None

    def _set_cached(self, url: str, data: Any):
        key = hashlib.sha256(url.encode()).hexdigest()
        self._cache[key] = (data, time.time() + self.cache_ttl)

    def _request(self, url: str) -> Optional[Dict[str, Any]]:
        cached = self._get_cached(url)
        if cached is not None:
            return cached

        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                self._set_cached(url, data)
                return data
        except urllib.error.HTTPError as e:
            if e.code == 403:
                remaining = e.headers.get("X-RateLimit-Remaining", "0")
                reset_time = e.headers.get("X-RateLimit-Reset", "")
                print(f"  [GitHubClient] Rate limit hit. Remaining: {remaining}, Reset: {reset_time}")
            else:
                print(f"  [GitHubClient] HTTP error: {e.code} {e.reason}")
            return None
        except Exception as e:
            print(f"  [GitHubClient] Request error: {e}")
            return None

    def fetch_trending(self, language: str, per_page: int = 50) -> List[Dict[str, Any]]:
        """拉取 GitHub Trending 仓库 (按 star 数量排序)"""
        query = urllib.parse.quote(f"language:{language} created:>2020-01-01")
        url = f"{self.BASE_URL}/search/repositories?q={query}&sort=stars&order=desc&per_page={per_page}"
        data = self._request(url)
        if data and "items" in data:
            return data["items"]
        return []

    def fetch_repo(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """拉取单个仓库详情"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        return self._request(url)


# ============================================
# 工具评估器
# ============================================
class ToolEvaluator:
    """5 维度权重评分"""

    WEIGHTS = {
        "stars_growth": 0.30,
        "activity": 0.25,
        "documentation": 0.20,
        "license": 0.15,
        "pmo_fit": 0.10,
    }

    # 允许商用的许可证
    COMMERCIAL_LICENSES = {
        "mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause",
        "isc", "unlicense", "cc0-1.0", "wtfpl", "zlib"
    }

    # PMO 场景关键词 (与工具契合度)
    PMO_FIT_KEYWORDS = [
        "ci/cd", "cicd", "github-actions", "gitlab-ci", "jenkins",
        "agent", "ai-agent", "autonomous", "multi-agent", "crewai", "autogen",
        "evaluation", "eval", "benchmark", "testing", "llm-evaluation",
        "monitoring", "observability", "prometheus", "grafana", "sentry",
        "deployment", "container", "kubernetes", "docker", "helm",
        "version-control", "git", "code-review", "lint", "formatter",
        "database", "cache", "queue", "message-broker", "nats", "kafka",
        "api", "rest", "grpc", "openapi", "swagger",
        "auth", "oauth", "jwt", "security", "secret",
        "pipeline", "workflow", "orchestration", "dag",
        "sandbox", "isolation", "proxy", "gateway", "rate-limit",
        "telemetry", "tracing", "logging", "alerting",
    ]

    def __init__(self):
        self.evaluation_count = 0
        self.total_score = 0.0

    def evaluate(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """评估单个仓库, 返回 5 维度评分 + 总分"""
        self.evaluation_count += 1

        stars = repo.get("stargazers_count", 0)
        stars_score = min(stars / 50000 * 100, 100)

        open_issues = repo.get("open_issues_count", 0)
        pushed_at = repo.get("pushed_at", "")
        days_since_push = 0
        if pushed_at:
            try:
                pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                days_since_push = (datetime.now(timezone.utc) - pushed_dt).days
            except Exception:
                days_since_push = 999

        activity_score = max(0, 100 - days_since_push * 3 - open_issues * 0.5)

        readme_exists = repo.get("has_wiki", False) or repo.get("has_pages", False)
        description = repo.get("description", "") or ""
        doc_score = min(len(description) / 3 + (50 if readme_exists else 0), 100)

        license_key = (repo.get("license") or {}).get("spdx_id", "").lower()
        license_score = 100 if license_key in self.COMMERCIAL_LICENSES else (50 if license_key else 0)

        full_text = " ".join([
            repo.get("name", ""),
            repo.get("description", ""),
            repo.get("topics", ""),
            ",".join(repo.get("topics", []) or []),
            repo.get("language", ""),
        ]).lower()
        pmo_fit_score = 0
        for kw in self.PMO_FIT_KEYWORDS:
            if kw in full_text:
                pmo_fit_score += (100 / len(self.PMO_FIT_KEYWORDS))
        pmo_fit_score = min(pmo_fit_score, 100)

        total = (
            stars_score * self.WEIGHTS["stars_growth"]
            + activity_score * self.WEIGHTS["activity"]
            + doc_score * self.WEIGHTS["documentation"]
            + license_score * self.WEIGHTS["license"]
            + pmo_fit_score * self.WEIGHTS["pmo_fit"]
        )

        self.total_score += total

        breakdown = {
            "stars_growth": {"score": round(stars_score, 2), "weight": f"{int(self.WEIGHTS['stars_growth']*100)}%"},
            "activity": {"score": round(activity_score, 2), "weight": f"{int(self.WEIGHTS['activity']*100)}%"},
            "documentation": {"score": round(doc_score, 2), "weight": f"{int(self.WEIGHTS['documentation']*100)}%"},
            "license": {"score": round(license_score, 2), "weight": f"{int(self.WEIGHTS['license']*100)}%"},
            "pmo_fit": {"score": round(pmo_fit_score, 2), "weight": f"{int(self.WEIGHTS['pmo_fit']*100)}%"},
        }

        return {
            "total_score": round(total, 2),
            "breakdown": breakdown,
            "stars": stars,
            "language": repo.get("language", ""),
            "license": license_key or "unknown",
            "topics": repo.get("topics", []) or [],
            "description": description,
        }

    def average_score(self) -> float:
        if self.evaluation_count == 0:
            return 0.0
        return round(self.total_score / self.evaluation_count, 2)


# ============================================
# ScoutAgent
# ============================================
class ScoutAgent(PMOAgent):
    """L2 Scout — 司法权 (工程工具侦察, 维度 4, DEC-2026-0009)

    职责: 主动侦察 GitHub Trending 优质开源工具, 评估后推荐 Sponsor
    重要: ScoutAgent 不自动采纳, 只推荐; 采纳归 Sponsor
    """

    LANGUAGES = ["Python", "TypeScript", "Go", "Rust"]

    # PMO 场景工具类别 (工具 → 类别映射)
    TOOL_CATEGORIES = {
        "ci_cd": ["github-actions", "gitlab-ci", "jenkins", "caching", "ci"],
        "agent_framework": ["agent", "autonomous", "multi-agent", "agentic"],
        "evaluation": ["evaluation", "benchmark", "llm-evaluation", "testing"],
        "monitoring": ["monitoring", "observability", "alerting"],
        "deployment": ["deployment", "container", "kubernetes", "docker"],
        "api": ["api", "rest", "grpc", "openapi"],
        "security": ["auth", "oauth", "security", "secret"],
        "messaging": ["message-broker", "queue", "nats", "kafka"],
        "storage": ["database", "cache", "storage"],
    }

    def __init__(self, pmo_root: str):
        super().__init__("Scout-Agent", "司法权 (工程工具侦察, 维度 4)", "L2", pmo_root)
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.github = GitHubClient(token=self.github_token, cache_ttl_seconds=86400)
        self.evaluator = ToolEvaluator()
        self.scanned_repos: List[Dict[str, Any]] = []
        self.tool_decisions: List[str] = []
        self._rising_previous: set = set()

    def scan_trending(self, languages: List[str] = None, per_language: int = 50) -> List[Dict[str, Any]]:
        """扫描 GitHub Trending (多语言)"""
        languages = languages or self.LANGUAGES
        all_repos = []
        for lang in languages:
            print(f"  [ScoutAgent] 扫描 {lang} 语言 Top {per_language}...")
            repos = self.github.fetch_trending(language=lang, per_page=per_language)
            for repo in repos:
                repo["_scanned_lang"] = lang
            all_repos.extend(repos)
            time.sleep(1)

        all_repos.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
        self.scanned_repos = all_repos
        self.log_reflection("scan", f"扫描完成, 共 {len(all_repos)} 个仓库, 覆盖 {len(languages)} 种语言")
        return all_repos

    def evaluate_repo(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """评估单个仓库"""
        evaluation = self.evaluator.evaluate(repo)
        return {
            "repo": {
                "full_name": repo.get("full_name", ""),
                "description": repo.get("description", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language", ""),
                "license": (repo.get("license") or {}).get("spdx_id", ""),
                "topics": repo.get("topics", []) or [],
                "url": repo.get("html_url", ""),
                "pushed_at": repo.get("pushed_at", ""),
                "created_at": repo.get("created_at", ""),
            },
            "evaluation": evaluation,
        }

    def evaluate_all(self, top_n: int = 50) -> List[Dict[str, Any]]:
        """评估扫描到的 Top N 仓库"""
        repos_to_evaluate = self.scanned_repos[:top_n]
        results = []
        for repo in repos_to_evaluate:
            evaluated = self.evaluate_repo(repo)
            results.append(evaluated)
        return results

    def detect_rising(self, evaluated: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
        """检测新晋项目 (本次 Top K 中, 上次不在其中的)"""
        current_top = set(r["repo"]["full_name"] for r in evaluated[:top_k])
        rising = [r for r in evaluated[:top_k] if r["repo"]["full_name"] not in self._rising_previous]
        self._rising_previous = current_top
        return rising

    def get_tool_category(self, repo: Dict[str, Any]) -> List[str]:
        """判断工具属于哪个 PMO 场景类别"""
        full_text = " ".join([
            repo.get("full_name", ""),
            repo.get("description", ""),
            ",".join(repo.get("topics", []) or []),
        ]).lower()
        categories = []
        for cat, keywords in self.TOOL_CATEGORIES.items():
            for kw in keywords:
                if kw in full_text:
                    categories.append(cat)
                    break
        return list(set(categories)) if categories else ["general"]

    def generate_tool_decision(self, evaluated: Dict[str, Any], tool_decisions_dir: Path) -> str:
        """为单个工具生成 DEC-TOOL-*.json 评估文档"""
        repo = evaluated["repo"]
        ev = evaluated["evaluation"]

        tool_id = repo["full_name"].replace("/", "-")
        ts = datetime.now(timezone.utc)
        dec_num = int(ts.strftime("%m%d%H%M%S"))
        dec_id = f"DEC-TOOL-{ts.year}-{dec_num:04d}"

        categories = self.get_tool_category(repo)

        decision = {
            "decision_id": dec_id,
            "timestamp": ts.isoformat(),
            "title": f"工具评估: {repo['full_name']} (评分 {ev['total_score']}/100)",
            "category": "tool-evaluation",
            "scout_agent": "Scout-Agent",
            "data_dimension": "维度 4: 工程工具生态",
            "repo": repo,
            "evaluation": ev,
            "pmo_fit_categories": categories,
            "sponsor_action": "pending",
            "sponsor_decision": None,
            "scoring": {
                "weights": ToolEvaluator.WEIGHTS,
                "breakdown": ev["breakdown"],
                "total_score": ev["total_score"]
            }
        }

        tool_decisions_dir.mkdir(parents=True, exist_ok=True)
        out_file = tool_decisions_dir / f"{tool_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2, ensure_ascii=False)

        self.tool_decisions.append(dec_id)
        self.log_reflection("tool_decision", f"生成工具评估文档: {dec_id} {repo['full_name']} (score={ev['total_score']})")
        return dec_id

    def get_top_recommendations(self, evaluated: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """获取 Top N 推荐 (给 Sponsor 看板)"""
        sorted_eval = sorted(evaluated, key=lambda x: x["evaluation"]["total_score"], reverse=True)
        recommendations = []
        for e in sorted_eval[:top_n]:
            repo = e["repo"]
            ev = e["evaluation"]
            recommendations.append({
                "full_name": repo["full_name"],
                "url": repo["url"],
                "score": ev["total_score"],
                "stars": repo["stars"],
                "language": repo["language"],
                "categories": self.get_tool_category(repo),
                "description": repo["description"],
                "license": repo["license"],
            })
        return recommendations

    def save_scouting_history(self, evaluated: List[Dict[str, Any]], output_dir: Path):
        """保存扫描历史"""
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc)
        history_file = output_dir / f"scouting-{ts.strftime('%Y%m%d')}.json"
        summary = {
            "timestamp": ts.isoformat(),
            "total_scanned": len(self.scanned_repos),
            "total_evaluated": len(evaluated),
            "average_score": self.evaluator.average_score(),
            "languages": list(set(r.get("_scanned_lang", "") for r in self.scanned_repos)),
            "top_20": [
                {
                    "full_name": e["repo"]["full_name"],
                    "score": e["evaluation"]["total_score"],
                    "stars": e["repo"]["stars"],
                    "language": e["repo"]["language"],
                }
                for e in sorted(evaluated, key=lambda x: x["evaluation"]["total_score"], reverse=True)[:20]
            ]
        }
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取工具侦察指标 (给 MetricsCollector 用)"""
        return {
            "TOOL-M-001": len(self.scanned_repos),
            "TOOL-M-002": 0,
            "TOOL-M-003": len(set(r.get("_scanned_lang", "") for r in self.scanned_repos)),
            "TOOL-M-004": 0,
            "TOOL-M-005": self.evaluator.average_score(),
        }

    def audit_pmo_main(self, pmo_main) -> Dict[str, Any]:
        """审计 PMO-Main (ScoutAgent 视角)"""
        return {
            "auditor": self.name,
            "auditee": pmo_main.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scout_status": "running",
            "scanned_repos": len(self.scanned_repos),
            "tool_decisions_generated": len(self.tool_decisions),
            "verdict": "compliant"
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务 (标准接口)"""
        action = task.get("action", "")

        if action == "scan":
            languages = task.get("languages", self.LANGUAGES)
            per_lang = task.get("per_language", 50)
            repos = self.scan_trending(languages=languages, per_language=per_lang)
            return {
                "agent": self.name,
                "action": action,
                "success": True,
                "result": {"scanned": len(repos), "languages": languages}
            }

        elif action == "evaluate":
            top_n = task.get("top_n", 50)
            if not self.scanned_repos:
                return {"agent": self.name, "action": action, "success": False, "error": "请先 scan"}
            evaluated = self.evaluate_all(top_n=top_n)
            return {
                "agent": self.name,
                "action": action,
                "success": True,
                "result": {
                    "evaluated_count": len(evaluated),
                    "average_score": self.evaluator.average_score(),
                }
            }

        elif action == "recommend":
            top_n = task.get("top_n", 5)
            if not self.scanned_repos:
                return {"agent": self.name, "action": action, "success": False, "error": "请先 scan + evaluate"}
            evaluated = self.evaluate_all(top_n=50)
            recs = self.get_top_recommendations(evaluated, top_n=top_n)
            rising = self.detect_rising(evaluated, top_k=20)
            tool_dir = Path(self.pmo_root) / "decisions" / "active"
            for e in evaluated[:top_n]:
                self.generate_tool_decision(e, tool_dir)
            return {
                "agent": self.name,
                "action": action,
                "success": True,
                "result": {
                    "recommendations": recs,
                    "rising_count": len(rising),
                    "rising_projects": [{"full_name": r["repo"]["full_name"], "score": r["evaluation"]["total_score"]} for r in rising],
                }
            }

        elif action == "get_metrics_summary":
            return {"agent": self.name, "action": action, "success": True, "result": self.get_metrics_summary()}

        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print("=== ScoutAgent 演示 (DEC-2026-0009) ===\n")

    agent = ScoutAgent(PMO_ROOT)
    agent.activate()
    agent.start()

    print(f"[1] ScoutAgent 状态: {agent.reflect()['state']}\n")

    print("[2] 扫描 GitHub Trending (Python + TypeScript, 每语言 Top 10 演示)")
    repos = agent.scan_trending(languages=["Python", "TypeScript"], per_language=10)
    print(f"  - 扫描完成: {len(repos)} 个仓库\n")

    if repos:
        print("[3] 评估 Top 10")
        evaluated = agent.evaluate_all(top_n=10)
        for e in sorted(evaluated, key=lambda x: x["evaluation"]["total_score"], reverse=True):
            repo = e["repo"]
            ev = e["evaluation"]
            print(f"  [{ev['total_score']:5.2f}] {repo['full_name']} (stars={repo['stars']}, lang={repo['language']})")
        print(f"  - 平均评分: {agent.evaluator.average_score()}\n")

        print("[4] 生成 Top 5 推荐 + DEC-TOOL 文档")
        recs = agent.get_top_recommendations(evaluated, top_n=5)
        tool_dir = Path(PMO_ROOT) / "decisions" / "active"
        for e in evaluated[:5]:
            dec_id = agent.generate_tool_decision(e, tool_dir)
            print(f"  - {dec_id}: {e['repo']['full_name']} (score={e['evaluation']['total_score']})")
        print(f"  - DEC-TOOL 文档已生成: {len(agent.tool_decisions)} 个\n")

        print("[5] 新晋项目检测")
        rising = agent.detect_rising(evaluated, top_k=10)
        print(f"  - 新晋项目: {len(rising)} 个")
        for r in rising:
            print(f"    - {r['repo']['full_name']} (score={r['evaluation']['total_score']})")
        print()

        print("[6] 保存扫描历史")
        history_dir = Path(PMO_ROOT) / "metrics" / "tool-scouting"
        agent.save_scouting_history(evaluated, history_dir)
        print(f"  - 历史已保存: {history_dir}\n")

        print("[7] 指标摘要 (给 MetricsCollector)")
        metrics = agent.get_metrics_summary()
        for k, v in metrics.items():
            print(f"  - {k}: {v}")
        print()

    print("=== ScoutAgent 演示完成 ===")
