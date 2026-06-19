"""
m2_7_self_test.py — m2.7 自测

验收点: 业务项目接入 PMO 5 步流程可演示
- L1: 5 步文档存在且完整 (biz-project-onboarding-5-steps.md)
- L2: 5 步内容覆盖 (注册/5阶段声明/业务配置/消息接入/PMO监管接入)
- L3: templates/ 包含所有必需模板
"""

import os
from pathlib import Path

PMO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_l1_onboarding_doc():
    """L1: 5 步文档存在且完整"""
    print("\n=== L1: 5 步文档 ===")
    doc = PMO_ROOT / "docs" / "biz-project-onboarding-5-steps.md"
    if not doc.exists():
        print(f"  ❌ biz-project-onboarding-5-steps.md 不存在")
        return False, 0, 0

    size = doc.stat().st_size
    content = doc.read_text()
    print(f"  ✅ 文档存在 ({size} bytes)")

    # 检查 5 步关键字
    steps = ["注册", "5 阶段", "业务配置", "消息机制", "PMO 监管"]
    found = sum(1 for s in steps if s in content)
    print(f"  ✅ 步骤关键字: {found}/5")
    return found >= 5, 2, (0 if found >= 5 else 1)


def test_l2_step_coverage():
    """L2: 5 步内容覆盖"""
    print("\n=== L2: 5 步内容覆盖 ===")
    doc = PMO_ROOT / "docs" / "biz-project-onboarding-5-steps.md"
    if not doc.exists():
        print(f"  ❌ 文档不存在")
        return False, 0, 1

    content = doc.read_text()
    checks = [
        ("注册", "业务项目注册"),
        ("5 阶段", "研发 5 阶段"),
        ("业务配置", "业务配置"),
        ("消息机制", "消息接入"),
        ("PMO 监管", "PMO 监管接入"),
    ]
    passed = 0
    for keyword, desc in checks:
        if keyword in content or desc in content:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")

    print(f"\n  L2 结果: {passed}/5")
    return passed >= 4, passed, (0 if passed >= 4 else 1)


def test_l3_templates():
    """L3: templates/ 包含所有必需模板"""
    print("\n=== L3: templates/ 必需模板 ===")
    templates_dir = PMO_ROOT / "biz-projects" / "templates"

    required = [
        "contract-project-overall.md",
        "contract-eng-5-stages.md",
        "contract-biz-ops-roles.md",
        "contract-biz-external-interface.md",
    ]
    # Check templates/eng-roles/ (not biz-projects/templates/eng-roles)
    pmo_templates = PMO_ROOT / "templates" / "eng-roles"
    required_pmo = [
        "01-requirement-engineer.template.md",
        "02-development-engineer.template.md",
        "03-test-engineer.template.md",
        "04-operations-engineer.template.md",
        "05-evaluation-engineer.template.md",
    ]

    passed = 0
    failed = 0
    for f in required:
        p = templates_dir / f
        if p.exists():
            print(f"  ✅ {f}")
            passed += 1
        else:
            print(f"  ❌ {f} 缺失")
            failed += 1
    for f in required_pmo:
        p = pmo_templates / f
        if p.exists():
            print(f"  ✅ templates/eng-roles/{f}")
            passed += 1
        else:
            print(f"  ❌ templates/eng-roles/{f} 缺失")
            failed += 1

    print(f"\n  L3 结果: {passed}/{passed + failed}")
    return failed == 0, passed, failed


def main():
    print("=" * 60)
    print("m2.7 业务项目接入流程 5 步 自测")
    print(f"PMO_ROOT: {PMO_ROOT}")
    print("=" * 60)

    l1_pass, l1_p, l1_f = test_l1_onboarding_doc()
    l2_pass, l2_p, l2_f = test_l2_step_coverage()
    l3_pass, l3_p, l3_f = test_l3_templates()

    total_pass = l1_p + l2_p + l3_p
    total_fail = l1_f + l2_f + l3_f
    total = total_pass + total_fail

    print("\n" + "=" * 60)
    print(f"m2.7 自测结果: {total_pass}/{total} 通过")
    print(f"  L1 (5 步文档): {'✅' if l1_pass else '❌'}")
    print(f"  L2 (步骤覆盖): {l2_p}/5 {'✅' if l2_pass else '❌'}")
    print(f"  L3 (必需模板): {l3_p}/{l3_p+l3_f} {'✅' if l3_pass else '❌'}")
    print("=" * 60)

    import json
    report = {
        "task": "m2.7",
        "version": "v0.14.0",
        "timestamp": "2026-06-19T13:05:00+08:00",
        "total": total,
        "passed": total_pass,
        "failed": total_fail,
        "overall": total_fail == 0,
    }
    report_dir = PMO_ROOT / "tests"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "m2.7-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
    return total_fail == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
