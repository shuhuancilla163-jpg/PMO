"""
m7_self_test.py — M7 工程实现层评估自测

验收: m7.1~m7.6 6 份评估报告全部可出。
"""

import os
import sys
from pathlib import Path

PMO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, str(PMO_ROOT / "scripts" / "runtime" / "evaluation"))

RESULTS = []


def check(name: str, condition: bool, detail: str) -> bool:
    icon = "✅" if condition else "❌"
    print(f"  {icon} {name}: {detail}")
    RESULTS.append({"name": name, "passed": condition, "detail": detail})
    return condition


def test_m71():
    """m7.1: agent 框架评估报告"""
    print("\n=== m7.1: agent 框架评估报告 ===")
    p = PMO_ROOT / "docs" / "evaluation" / "m7.1.json"
    ok = p.exists() and p.stat().st_size > 1000
    check("m7.1 报告存在", ok, f"{p.stat().st_size if ok else 0} bytes")
    if ok:
        import json
        data = json.loads(p.read_text())
        candidates = data.get("summary", {}).get("candidate_count", 0)
        capabilities = data.get("summary", {}).get("capability_count", 0)
        check("候选框架 ≥ 3", candidates >= 3, f"{candidates} 个")
        check("能力覆盖 ≥ 5", capabilities >= 5, f"{capabilities} 项")
        recs = data.get("recommendations", [])
        check("推荐结论存在", len(recs) >= 1, f"{len(recs)} 条")
    return ok


def test_m72():
    """m7.2: 工具层评估报告"""
    print("\n=== m7.2: 工具层评估报告 ===")
    p = PMO_ROOT / "docs" / "evaluation" / "m7.2.json"
    ok = p.exists() and p.stat().st_size > 1000
    check("m7.2 报告存在", ok, f"{p.stat().st_size if ok else 0} bytes")
    if ok:
        import json
        data = json.loads(p.read_text())
        candidates = data.get("summary", {}).get("candidate_count", 0)
        capabilities = data.get("summary", {}).get("capability_count", 0)
        check("候选工具 ≥ 3", candidates >= 3, f"{candidates} 个")
        check("工具能力覆盖 ≥ 10", capabilities >= 10, f"{capabilities} 项")
    return ok


def test_m73():
    """m7.3: 部署评估报告"""
    print("\n=== m7.3: 部署评估报告 ===")
    p = PMO_ROOT / "docs" / "evaluation" / "m7.3.json"
    ok = p.exists() and p.stat().st_size > 500
    check("m7.3 报告存在", ok, f"{p.stat().st_size if ok else 0} bytes")
    if ok:
        import json
        data = json.loads(p.read_text())
        candidates = data.get("summary", {}).get("candidate_count", 0)
        check("候选部署方案 ≥ 3", candidates >= 3, f"{candidates} 个")
    return ok


def test_m74():
    """m7.4: 模型评估报告"""
    print("\n=== m7.4: 模型评估报告 ===")
    p = PMO_ROOT / "docs" / "evaluation" / "m7.4.json"
    ok = p.exists() and p.stat().st_size > 1000
    check("m7.4 报告存在", ok, f"{p.stat().st_size if ok else 0} bytes")
    if ok:
        import json
        data = json.loads(p.read_text())
        candidates = data.get("summary", {}).get("candidate_count", 0)
        check("候选模型 ≥ 3", candidates >= 3, f"{candidates} 个")
    return ok


def test_m75():
    """m7.5: 存储评估报告"""
    print("\n=== m7.5: 存储评估报告 ===")
    p = PMO_ROOT / "docs" / "evaluation" / "m7.5.json"
    ok = p.exists() and p.stat().st_size > 1000
    check("m7.5 报告存在", ok, f"{p.stat().st_size if ok else 0} bytes")
    if ok:
        import json
        data = json.loads(p.read_text())
        candidates = data.get("summary", {}).get("candidate_count", 0)
        capabilities = data.get("summary", {}).get("capability_count", 0)
        check("候选存储方案 ≥ 3", candidates >= 3, f"{candidates} 个")
        check("存储能力覆盖 ≥ 5", capabilities >= 5, f"{capabilities} 项")
    return ok


def test_m76():
    """m7.6: PMO 工程实现层推荐报告"""
    print("\n=== m7.6: PMO 工程实现层推荐报告 ===")
    p = PMO_ROOT / "docs" / "evaluation" / "m7.6.json"
    ok = p.exists() and p.stat().st_size > 500
    check("m7.6 报告存在", ok, f"{p.stat().st_size if ok else 0} bytes")
    if ok:
        import json
        data = json.loads(p.read_text())
        candidates = data.get("summary", {}).get("candidate_count", 0)
        capabilities = data.get("summary", {}).get("capability_count", 0)
        recs = data.get("recommendations", [])
        check("5 层技术栈候选", candidates >= 5, f"{candidates} 层")
        check("工程指标覆盖", capabilities >= 5, f"{capabilities} 项")
        check("推荐结论存在", len(recs) >= 1, f"{len(recs)} 条")
    return ok


def test_evaluation_framework():
    """evaluation.py 框架可工作"""
    print("\n=== evaluation.py 框架 ===")
    try:
        sys.path.insert(0, str(PMO_ROOT / "scripts" / "runtime" / "evaluation"))
        from evaluation import generate_all_reports
        reports = generate_all_reports()
        ok = len(reports) == 6 and all(k in reports for k in ["m7.1","m7.2","m7.3","m7.4","m7.5","m7.6"])
        check("generate_all_reports() 返回 6 份报告", ok, f"{len(reports)} 份")
        return ok
    except Exception as e:
        check("evaluation.py 可导入", False, str(e)[:80])
        return False


def main():
    print("=" * 60)
    print("M7 工程实现层评估 自测")
    print(f"PMO_ROOT: {PMO_ROOT}")
    print("=" * 60)

    results = [
        test_evaluation_framework(),
        test_m71(),
        test_m72(),
        test_m73(),
        test_m74(),
        test_m75(),
        test_m76(),
    ]

    passed = sum(1 for r in results if r)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"M7 自测结果: {passed}/{total} 通过")
    for i, r in enumerate(results, 1):
        task = ["框架", "m7.1", "m7.2", "m7.3", "m7.4", "m7.5", "m7.6"][i-1]
        print(f"  {'✅' if r else '❌'} {task}")
    print("=" * 60)

    import json
    report = {
        "task": "M7",
        "version": "v0.14.0",
        "timestamp": "2026-06-19T14:29:00+08:00",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "overall": passed == total,
        "checks": [{"name": ["框架", "m7.1", "m7.2", "m7.3", "m7.4", "m7.5", "m7.6"][i], "passed": r}
                   for i, r in enumerate(results)],
    }
    report_dir = PMO_ROOT / "tests"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "M7-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
