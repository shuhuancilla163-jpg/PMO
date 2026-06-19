"""
PMO 阈值考核引擎 (threshold_engine.py, m0.9, DEC-2026-0009)
- 加载 config/thresholds.yaml，支持按项目覆盖
- 比对指标值与阈值，返回 ok/warn/critical
- 计算 3 维度加权得分
- 生成考核报告，写入 reports/assessments/<project_id>/
- 定时跑批（每 6 小时）+ 手动触发
"""
import json
import os
import sys
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Verdict(str):
    """判定结果"""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    NO_DATA = "no_data"


class ThresholdEngine:
    """PMO 阈值考核引擎（轻量版考核闭环）

    核心流程:
    1. 加载阈值配置（PMO 默认 + 项目覆盖）
    2. 采集指标值（从 MetricsCollector 或直接传入）
    3. 比对阈值，判定每项指标
    4. 计算 3 维度加权得分
    5. 生成考核报告

    不做:
    - 自动扣分（记录违规，不自动扣分）
    - 告警（委托 OperationsMonitor）
    """

    PROTOCOL_VERSION = "0.9.0"

    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.thresholds_file = self.pmo_root / "config" / "thresholds.yaml"
        self.reports_dir = self.pmo_root / "reports" / "assessments"
        self.metrics_dir = self.pmo_root / "metrics"
        self.biz_projects_dir = self.pmo_root / "biz-projects"

        # 内存缓存
        self._thresholds_cache: Dict[str, Any] = {}
        self._thresholds_cache_mtime: float = 0

        # 报告序号
        self._report_seq = 0
        self._load_report_seq()

    # ---------------- 阈值加载 ----------------

    def load_thresholds(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """加载阈值配置（PMO 默认 + 项目覆盖）

        优先级: 项目级 reports/thresholds.yaml > config/thresholds.yaml
        """
        cache_key = project_id or "__global__"
        mtime = self.thresholds_file.stat().st_mtime if self.thresholds_file.exists() else 0

        if cache_key in self._thresholds_cache and self._thresholds_cache_mtime == mtime:
            return self._thresholds_cache[cache_key]

        # PMO 默认
        default_thresholds = self._load_yaml(self.thresholds_file)

        # 项目级覆盖
        if project_id:
            proj_threshold_file = (
                self.biz_projects_dir / project_id / "reports" / "thresholds.yaml"
            )
            if proj_threshold_file.exists():
                proj_thresholds = self._load_yaml(proj_threshold_file)
                default_thresholds = self._deep_merge(default_thresholds, proj_thresholds)

        self._thresholds_cache[cache_key] = default_thresholds
        self._thresholds_cache_mtime = mtime
        return default_thresholds

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并 override 到 base"""
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    # ---------------- 阈值比对 ----------------

    def evaluate_metric(self, metric_id: str, value: float,
                        project_id: Optional[str] = None) -> Dict[str, Any]:
        """比对单个指标值与阈值

        Args:
            metric_id: 指标 ID（如 "flow_latency"）
            value: 当前值
            project_id: 业务项目 ID（用于加载项目级阈值覆盖）

        Returns:
            {
                "metric_id": "flow_latency",
                "value": 250,
                "threshold_warn": 200,
                "threshold_critical": 300,
                "direction": "lower_is_better",
                "verdict": "warning",
                "exceeded_by": 50
            }
        """
        thresholds = self.load_thresholds(project_id)

        # 在 3 类阈值中查找
        threshold_def = None
        for cat_key in ["business_thresholds", "governance_thresholds", "engineering_thresholds"]:
            cat = thresholds.get(cat_key, {})
            if metric_id in cat:
                threshold_def = cat[metric_id]
                threshold_def["_category"] = cat_key
                break

        if threshold_def is None:
            return {
                "metric_id": metric_id,
                "value": value,
                "verdict": Verdict.NO_DATA,
                "error": f"metric '{metric_id}' not found in thresholds.yaml"
            }

        warn = threshold_def.get("warn")
        critical = threshold_def.get("critical")
        direction = threshold_def.get("direction", "lower_is_better")

        verdict = self._compute_verdict(value, warn, critical, direction)
        exceeded_by = None
        if verdict == Verdict.WARNING:
            if direction == "lower_is_better":
                exceeded_by = round(value - warn, 4)
            else:
                exceeded_by = round(warn - value, 4)
        elif verdict == Verdict.CRITICAL:
            if direction == "lower_is_better":
                exceeded_by = round(value - critical, 4)
            else:
                exceeded_by = round(critical - value, 4)

        return {
            "metric_id": metric_id,
            "value": value,
            "unit": threshold_def.get("unit", "unknown"),
            "threshold_warn": warn,
            "threshold_critical": critical,
            "direction": direction,
            "verdict": verdict.value,
            "exceeded_by": exceeded_by,
            "description": threshold_def.get("description", ""),
            "_category": threshold_def["_category"]
        }

    def _compute_verdict(self, value: float, warn: float, critical: float,
                         direction: str) -> Verdict:
        if direction == "lower_is_better":
            if value >= critical:
                return Verdict.CRITICAL
            elif value >= warn:
                return Verdict.WARNING
            else:
                return Verdict.OK
        else:  # higher_is_better
            if value <= critical:
                return Verdict.CRITICAL
            elif value <= warn:
                return Verdict.WARNING
            else:
                return Verdict.OK

    # ---------------- 指标采集 ----------------

    def collect_project_metrics(self, project_id: str) -> Dict[str, float]:
        """从 metrics/ 目录采集业务项目的最新指标值

        读取 metrics/business/<project_id>/ 下最新指标文件
        """
        metrics = {}
        proj_metrics_dir = self.metrics_dir / "business" / project_id

        if not proj_metrics_dir.exists():
            return metrics

        # 找最新的指标文件
        metric_files = sorted(proj_metrics_dir.rglob("*.json"), key=lambda p: p.stat().st_mtime)
        if not metric_files:
            return metrics

        latest = metric_files[-1]
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            # 提取 5 项基础业务指标
            biz_5 = ["flow_latency", "exception_rate", "pass_rate", "rollback_rate", "token_consumption"]
            for m in biz_5:
                if m in data:
                    metrics[m] = data[m]
        except Exception:
            pass

        return metrics

    # ---------------- 项目考核 ----------------

    def evaluate_project(self, project_id: str,
                        metrics: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """考核单个业务项目的全部指标

        Args:
            project_id: 业务项目 ID
            metrics: 可选，直接传入指标字典（绕过采集）

        Returns:
            3 维度考核结果
        """
        if metrics is None:
            metrics = self.collect_project_metrics(project_id)

        thresholds = self.load_thresholds(project_id)

        # 3 维度
        dimension_1 = self._evaluate_dimension(
            project_id, metrics, thresholds, "governance_thresholds",
            thresholds.get("assessment_weights", {}).get("dimension_1_metrics", {})
        )
        dimension_2 = self._evaluate_dimension(
            project_id, metrics, thresholds, "engineering_thresholds",
            thresholds.get("assessment_weights", {}).get("dimension_2_metrics", {})
        )
        dimension_3 = self._evaluate_dimension(
            project_id, metrics, thresholds, "business_thresholds",
            thresholds.get("assessment_weights", {}).get("dimension_3_metrics", {})
        )

        # 维度得分
        d1_score = dimension_1["score"]
        d2_score = dimension_2["score"]
        d3_score = dimension_3["score"]

        weights = thresholds.get("assessment_weights", {})
        d1_w = weights.get("dimension_1_weight", 0.30)
        d2_w = weights.get("dimension_2_weight", 0.30)
        d3_w = weights.get("dimension_3_weight", 0.40)

        overall_score = d1_score * d1_w + d2_score * d2_w + d3_score * d3_w

        # 整体判定
        assessment_rules = thresholds.get("assessment_rules", {}).get("overall_verdict", {})
        overall_verdict = self._overall_verdict(overall_score, assessment_rules)

        # 违规列表
        all_violations = (
            dimension_1["violations"]
            + dimension_2["violations"]
            + dimension_3["violations"]
        )

        return {
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_evaluated": list(metrics.keys()),
            "dimension_1": dimension_1,
            "dimension_2": dimension_2,
            "dimension_3": dimension_3,
            "overall_score": round(overall_score, 2),
            "overall_verdict": overall_verdict,
            "violations": all_violations,
            "violation_count": len(all_violations),
            "metrics_source": "collected" if metrics else "none"
        }

    def _evaluate_dimension(self, project_id: str, metrics: Dict[str, float],
                           thresholds: Dict[str, Any], dim_key: str,
                           metric_weights: Dict[str, float]) -> Dict[str, Any]:
        """计算单个维度的得分和违规"""
        dim_thresholds = thresholds.get(dim_key, {})
        evaluations = {}
        violations = []
        total_weight = 0.0
        weighted_score = 0.0

        for metric_id, weight in metric_weights.items():
            if metric_id not in metrics:
                evaluations[metric_id] = {
                    "verdict": Verdict.NO_DATA.value,
                    "value": None,
                    "weight": weight
                }
                total_weight += weight
                continue

            value = metrics[metric_id]
            eval_result = self.evaluate_metric(metric_id, value, project_id)
            verdict = eval_result["verdict"]

            # 得分：ok=100, warning=60, critical=20, no_data=0
            verdict_scores = {
                Verdict.OK.value: 100,
                Verdict.WARNING.value: 60,
                Verdict.CRITICAL.value: 20,
                Verdict.NO_DATA.value: 0
            }
            score = verdict_scores.get(verdict, 0)

            evaluations[metric_id] = {
                "value": value,
                "verdict": verdict,
                "threshold_warn": eval_result.get("threshold_warn"),
                "threshold_critical": eval_result.get("threshold_critical"),
                "exceeded_by": eval_result.get("exceeded_by"),
                "weight": weight,
                "score": score
            }

            weighted_score += score * weight
            total_weight += weight

            if verdict in (Verdict.WARNING.value, Verdict.CRITICAL.value):
                violations.append({
                    "metric_id": metric_id,
                    "dimension": dim_key,
                    "verdict": verdict,
                    "value": value,
                    "threshold_warn": eval_result.get("threshold_warn"),
                    "threshold_critical": eval_result.get("threshold_critical"),
                    "exceeded_by": eval_result.get("exceeded_by"),
                    "direction": eval_result.get("direction")
                })

        dimension_score = (weighted_score / total_weight) if total_weight > 0 else 0

        # 维度判定
        dim_rules = thresholds.get("assessment_rules", {}).get("dimension_verdict", {})
        dim_verdict = self._dimension_verdict(dimension_score, dim_rules)

        return {
            "score": round(dimension_score, 2),
            "verdict": dim_verdict,
            "evaluations": evaluations,
            "violations": violations,
            "violation_count": len(violations),
            "coverage": round(total_weight, 2)
        }

    def _dimension_verdict(self, score: float, rules: Dict[str, str]) -> str:
        if score >= 80:
            return "compliant"
        elif score >= 60:
            return "warning"
        else:
            return "violation"

    def _overall_verdict(self, score: float, rules: Dict[str, str]) -> str:
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "warning"
        else:
            return "violation"

    # ---------------- 考核报告 ----------------

    def generate_assessment_report(self, project_id: str,
                                   metrics: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """生成考核报告并写入文件"""
        self._report_seq += 1
        report_id = f"ASSESS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{self._report_seq:03d}"

        result = self.evaluate_project(project_id, metrics)
        result["report_id"] = report_id

        # 写报告文件
        proj_report_dir = self.reports_dir / project_id
        proj_report_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
        report_file = proj_report_dir / f"{ts}.json"
        report_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        # 写 latest.json
        latest_file = proj_report_dir / "latest.json"
        latest_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        # 持久化序号
        self._save_report_seq()

        return result

    def _load_report_seq(self):
        seq_file = self.reports_dir / ".report_seq"
        try:
            if seq_file.exists():
                self._report_seq = int(seq_file.read_text().strip())
        except Exception:
            self._report_seq = 0

    def _save_report_seq(self):
        seq_file = self.reports_dir / ".report_seq"
        seq_file.parent.mkdir(parents=True, exist_ok=True)
        seq_file.write_text(str(self._report_seq))

    # ---------------- 定时跑批 ----------------

    def get_active_projects(self) -> List[str]:
        """获取所有 active 状态业务项目"""
        active = []
        if not self.biz_projects_dir.exists():
            return active
        for proj_dir in self.biz_projects_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            reg_file = proj_dir / "register.yaml"
            if reg_file.exists():
                try:
                    data = self._load_yaml(reg_file)
                    state = data.get("pmo_supervision", {}).get("state", "")
                    if state == "active":
                        active.append(proj_dir.name)
                except Exception:
                    pass
        return sorted(active)

    def run_periodic_assessment(self) -> Dict[str, Any]:
        """定时跑批：考核所有 active 项目"""
        active_projects = self.get_active_projects()
        results = {}
        for pid in active_projects:
            report = self.generate_assessment_report(pid)
            results[pid] = {
                "report_id": report["report_id"],
                "overall_verdict": report["overall_verdict"],
                "overall_score": report["overall_score"],
                "violation_count": report["violation_count"]
            }

        # 生成汇总报告
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "projects_assessed": len(active_projects),
            "projects": active_projects,
            "results": results,
            "period": "6h"
        }

        summary_file = self.reports_dir / "latest-summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        return summary

    def check_thresholds(self, project_id: str) -> Dict[str, Any]:
        """主动检查单个项目的指标超阈值情况（即时比对）"""
        metrics = self.collect_project_metrics(project_id)
        if not metrics:
            return {
                "project_id": project_id,
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "alert_triggered": False,
                "violations": [],
                "note": "no metrics collected"
            }

        thresholds = self.load_thresholds(project_id)
        violations = []
        for metric_id, value in metrics.items():
            eval_result = self.evaluate_metric(metric_id, value, project_id)
            if eval_result["verdict"] in (Verdict.WARNING.value, Verdict.CRITICAL.value):
                violations.append(eval_result)

        alert_triggered = any(v["verdict"] == Verdict.CRITICAL.value for v in violations)

        return {
            "project_id": project_id,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "metrics_checked": list(metrics.keys()),
            "violations": violations,
            "alert_triggered": alert_triggered,
            "violation_count": len(violations)
        }

    def get_latest_report(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取最新考核报告"""
        latest_file = self.reports_dir / project_id / "latest.json"
        if not latest_file.exists():
            return None
        try:
            return json.loads(latest_file.read_text(encoding="utf-8"))
        except Exception:
            return None


# ============================================
# 演示 / 自测入口
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("=== PMO ThresholdEngine 演示 (m0.9, DEC-2026-0009) ===\n")

    engine = ThresholdEngine(PMO_ROOT)

    # 1. 加载阈值
    print("[1] 加载阈值配置")
    thresholds = engine.load_thresholds()
    print(f"  - business_thresholds: {list(thresholds.get('business_thresholds', {}).keys())}")
    print(f"  - governance_thresholds: {list(thresholds.get('governance_thresholds', {}).keys())}")
    print(f"  - engineering_thresholds: {list(thresholds.get('engineering_thresholds', {}).keys())}")
    print()

    # 2. 比对单个指标
    print("[2] 比对单个指标")
    cases = [
        ("flow_latency", 150, "正常"),
        ("flow_latency", 250, "warn"),
        ("flow_latency", 350, "critical"),
        ("pass_rate", 0.95, "正常"),
        ("pass_rate", 0.85, "warn"),
        ("pass_rate", 0.75, "critical"),
    ]
    for metric_id, value, expected in cases:
        r = engine.evaluate_metric(metric_id, value)
        print(f"  {metric_id}={value} → verdict={r['verdict']} (expected={expected})")
    print()

    # 3. 主动检查阈值（使用模拟数据）
    print("[3] 主动检查阈值（1.1-pmo-self）")
    check = engine.check_thresholds("1.1-pmo-self")
    print(f"  - violation_count: {check['violation_count']}")
    print(f"  - alert_triggered: {check['alert_triggered']}")
    print()

    # 4. 生成考核报告（使用模拟指标）
    print("[4] 生成考核报告（1.1-pmo-self，模拟指标）")
    mock_metrics = {
        "flow_latency": 180,
        "exception_rate": 0.03,
        "pass_rate": 0.92,
        "rollback_rate": 0.015,
        "token_consumption": 4500,
    }
    report = engine.generate_assessment_report("1.1-pmo-self", mock_metrics)
    print(f"  - report_id: {report['report_id']}")
    print(f"  - overall_score: {report['overall_score']}")
    print(f"  - overall_verdict: {report['overall_verdict']}")
    print(f"  - dimension_1: score={report['dimension_1']['score']}, verdict={report['dimension_1']['verdict']}")
    print(f"  - dimension_2: score={report['dimension_2']['score']}, verdict={report['dimension_2']['verdict']}")
    print(f"  - dimension_3: score={report['dimension_3']['score']}, verdict={report['dimension_3']['verdict']}")
    print(f"  - violation_count: {report['violation_count']}")
    print()

    # 5. 获取 active 项目列表
    print("[5] Active 项目列表")
    active = engine.get_active_projects()
    print(f"  - count: {len(active)}")
    for pid in active:
        print(f"  - {pid}")
    print()

    print("=== ThresholdEngine 演示完成 ===")
