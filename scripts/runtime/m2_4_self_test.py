"""
m2_4_self_test.py — m2.4 自测

验收点:
- H1: 业务 SOP 模板可查 (templates/biz-docs/ 4 份模板)
- H2: 4 类异常定义可查 (exception-handling 模板)
- H3: 业务回滚粒度留接口 (biz-flow.md 框架态)
- H4: 业务流编排留接口 (biz-flow.md 框架态)
"""

import os
from pathlib import Path

PMO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_h1_sop_templates():
    """H1: 业务 SOP 模板可查"""
    print("\n=== H1: 业务 SOP 模板 ===")
    passed = 0
    failed = 0

    template_dir = PMO_ROOT / "biz-projects" / "templates" / "biz-docs"
    required = [
        ("01-requirements", "01-biz-requirements.template.md"),
        ("02-design", "02-biz-design.template.md"),
        ("03-implementation", "03-biz-flow.template.md"),
        ("03-implementation", "04-exception-handling.template.md"),
        ("04-release", "04-release-notes.template.md"),
    ]

    for subdir, filename in required:
        p = template_dir / subdir / filename
        if p.exists():
            size = p.stat().st_size
            print(f"  ✅ {subdir}/{filename} ({size} bytes)")
            passed += 1
        else:
            print(f"  ❌ {subdir}/{filename} 缺失")
            failed += 1

    print(f"\n  H1 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_h2_exception_handling():
    """H2: 4 类异常定义可查"""
    print("\n=== H2: 4 类异常定义 ===")
    passed = 0
    failed = 0

    exc_file = PMO_ROOT / "biz-projects" / "templates" / "biz-docs" / "03-implementation" / "04-exception-handling.template.md"
    if exc_file.exists():
        content = exc_file.read_text()
        required = ["BizException", "DataException", "IntegrationException", "SystemException"]
        for exc in required:
            if exc in content:
                print(f"  ✅ {exc} 定义存在")
                passed += 1
            else:
                print(f"  ❌ {exc} 缺失")
                failed += 1
    else:
        print(f"  ❌ exception-handling 模板不存在")
        failed += 1

    print(f"\n  H2 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_h3_rollback_granularity():
    """H3: 业务回滚粒度留接口"""
    print("\n=== H3: 业务回滚粒度接口 ===")
    passed = 0
    failed = 0

    flow_file = PMO_ROOT / "biz-projects" / "1.x-biz-template" / "biz-docs" / "03-implementation" / "biz-flow.md"
    if flow_file.exists():
        content = flow_file.read_text()
        if "回滚" in content or "rollback" in content.lower():
            print(f"  ✅ 回滚粒度接口存在")
            passed += 1
        else:
            print(f"  ❌ 回滚粒度接口缺失")
            failed += 1
        if "单事务回滚" in content or "补偿事务" in content or "全量回滚" in content:
            print(f"  ✅ 回滚粒度类型列出")
            passed += 1
        else:
            print(f"  ❌ 回滚粒度类型缺失")
            failed += 1
    else:
        print(f"  ❌ biz-flow.md 不存在")
        failed += 2

    print(f"\n  H3 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_h4_biz_flow_orchestration():
    """H4: 业务流编排留接口"""
    print("\n=== H4: 业务流编排接口 ===")
    passed = 0
    failed = 0

    flow_file = PMO_ROOT / "biz-projects" / "1.x-biz-template" / "biz-docs" / "03-implementation" / "biz-flow.md"
    if flow_file.exists():
        content = flow_file.read_text()
        interfaces = ["编排入口", "agent 顺序", "输入输出", "触发条件"]
        found = 0
        for interface in interfaces:
            if interface in content:
                print(f"  ✅ {interface} 接口存在")
                passed += 1
                found += 1
            else:
                print(f"  ⚠️ {interface} 接口缺失")
        if found >= 2:
            print(f"  ✅ 业务流编排接口留好 (≥2 项)")
            passed += 1
        else:
            print(f"  ❌ 业务流编排接口不足")
            failed += 1
    else:
        print(f"  ❌ biz-flow.md 不存在")
        failed += 3

    print(f"\n  H4 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def main():
    print("=" * 60)
    print("m2.4 业务执行层骨架 4 项 自测")
    print(f"PMO_ROOT: {PMO_ROOT}")
    print("=" * 60)

    h1_pass, h1_p, h1_f = test_h1_sop_templates()
    h2_pass, h2_p, h2_f = test_h2_exception_handling()
    h3_pass, h3_p, h3_f = test_h3_rollback_granularity()
    h4_pass, h4_p, h4_f = test_h4_biz_flow_orchestration()

    total_pass = h1_p + h2_p + h3_p + h4_p
    total_fail = h1_f + h2_f + h3_f + h4_f
    total = total_pass + total_fail

    print("\n" + "=" * 60)
    print(f"m2.4 自测结果: {total_pass}/{total} 通过")
    print(f"  H1 (SOP 模板): {h1_p}/{h1_p+h1_f} {'✅' if h1_pass else '❌'}")
    print(f"  H2 (异常定义): {h2_p}/{h2_p+h2_f} {'✅' if h2_pass else '❌'}")
    print(f"  H3 (回滚粒度): {h3_p}/{h3_p+h3_f} {'✅' if h3_pass else '❌'}")
    print(f"  H4 (流编排接口): {h4_p}/{h4_p+h4_f} {'✅' if h4_pass else '❌'}")
    print("=" * 60)

    import json
    report = {
        "task": "m2.4",
        "version": "v0.14.0",
        "timestamp": "2026-06-19T13:05:00+08:00",
        "total_tests": total,
        "passed": total_pass,
        "failed": total_fail,
        "tests": [
            {"name": "H1_sop_templates", "passed": h1_pass, "count": h1_p + h1_f, "sub_pass": h1_p},
            {"name": "H2_exception_handling", "passed": h2_pass, "count": h2_p + h2_f, "sub_pass": h2_p},
            {"name": "H3_rollback_granularity", "passed": h3_pass, "count": h3_p + h3_f, "sub_pass": h3_p},
            {"name": "H4_biz_flow_orchestration", "passed": h4_pass, "count": h4_p + h4_f, "sub_pass": h4_p},
        ],
        "overall": total_fail == 0,
    }
    report_dir = PMO_ROOT / "tests"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "m2.4-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
    return total_fail == 0


if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)
