"""
m2_3_self_test.py — m2.3 自测

验收点:
- G1: 5 阶段 agent 骨架模板可查 (templates/eng-roles/ 5 份)
- G2: biz-agents 框架结构可查 (1.x-biz-template/biz-agents/ + 1.x-examples/ 参考)
- G3: 5 阶段 agent 可激活演示 (1.1-pmo-self 实例)
"""

import os
import sys
import importlib
import importlib.machinery
from pathlib import Path

PMO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_g1_5stage_templates():
    """G1: 5 阶段 agent 骨架模板可查"""
    print("\n=== G1: 5 阶段 agent 骨架模板 ===")
    passed = 0
    failed = 0

    template_dir = PMO_ROOT / "templates" / "eng-roles"
    required_files = [
        "01-requirement-engineer.template.md",
        "02-development-engineer.template.md",
        "03-test-engineer.template.md",
        "04-operations-engineer.template.md",
        "05-evaluation-engineer.template.md",
        "README.md",
        "pmo-7-compliance-check.template.md",
    ]

    for f in required_files:
        p = template_dir / f
        if p.exists():
            size = p.stat().st_size
            print(f"  ✅ {f} ({size} bytes)")
            passed += 1
        else:
            print(f"  ❌ {f} 缺失")
            failed += 1

    # Check template content mentions 0.0.13
    readme = template_dir / "README.md"
    if readme.exists():
        content = readme.read_text()
        if "0.0.13" in content or "5 阶段" in content:
            print(f"  ✅ README 引用 0.0.13 / 5 阶段")
            passed += 1
        else:
            print(f"  ⚠️ README 未明确引用 0.0.13")
            failed += 1

    print(f"\n  G1 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_g2_biz_agents_framework():
    """G2: biz-agents 框架结构可查"""
    print("\n=== G2: biz-agents 框架结构 ===")
    passed = 0
    failed = 0

    # 1.x-biz-template biz-agents/
    template_agents = PMO_ROOT / "biz-projects" / "1.x-biz-template" / "biz-agents"
    if template_agents.exists():
        print(f"  ✅ 1.x-biz-template/biz-agents/ 存在")
        passed += 1
    else:
        print(f"  ❌ 1.x-biz-template/biz-agents/ 不存在")
        failed += 1

    readme = template_agents / "README.md"
    if readme.exists():
        size = readme.stat().st_size
        print(f"  ✅ README.md ({size} bytes)")
        passed += 1
        content = readme.read_text()
        if "框架态" in content or "template" in content.lower():
            print(f"  ✅ README 明确框架态")
            passed += 1
        else:
            print(f"  ⚠️ README 未明确框架态")
            failed += 1
    else:
        print(f"  ❌ README.md 不存在")
        failed += 1

    # biz-agents 下无 .py 文件 (空框架态)
    py_files = list(template_agents.glob("*.py"))
    if len(py_files) == 0:
        print(f"  ✅ 框架态: 无 .py 文件 (空目录)")
        passed += 1
    else:
        print(f"  ❌ 框架态: 仍有 {len(py_files)} 个 .py 文件")
        failed += 1

    # 1.x-examples/quant-finance/biz-agents/
    example_agents = PMO_ROOT / "biz-projects" / "1.x-examples" / "quant-finance" / "biz-agents"
    if example_agents.exists():
        py_files = list(example_agents.glob("*.py"))
        if len(py_files) > 0:
            print(f"  ✅ 1.x-examples/quant-finance/biz-agents/ 参考示例 ({len(py_files)} 个 agent)")
            passed += 1
        else:
            print(f"  ❌ 参考示例目录为空")
            failed += 1
        readme = example_agents / "README.md"
        if readme.exists():
            print(f"  ✅ 参考示例 README 存在")
            passed += 1
        else:
            print(f"  ❌ 参考示例 README 缺失")
            failed += 1
    else:
        print(f"  ❌ 1.x-examples/quant-finance/biz-agents/ 不存在")
        failed += 1

    print(f"\n  G2 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_g3_5stage_activation():
    """G3: 5 阶段 agent 可激活演示"""
    print("\n=== G3: 5 阶段 agent 可激活演示 ===")
    passed = 0
    failed = 0

    eng_roles_dir = PMO_ROOT / "biz-projects" / "1.1-pmo-self" / "eng-roles"
    required_agents = [
        "01-requirement-engineer.py",
        "02-development-engineer.py",
        "03-test-engineer.py",
        "04-operations-engineer.py",
        "05-evaluation-engineer.py",
    ]

    for f in required_agents:
        p = eng_roles_dir / f
        if p.exists():
            size = p.stat().st_size
            print(f"  ✅ {f} ({size} bytes)")
            passed += 1
        else:
            print(f"  ❌ {f} 缺失")
            failed += 1

    # Try importing each agent (use SourceFileLoader for hyphenated filenames)
    agent_modules = [
        ("01-requirement-engineer", "RequirementEngineer"),
        ("02-development-engineer", "DevelopmentEngineer"),
        ("03-test-engineer", "TestEngineer"),
        ("04-operations-engineer", "OperationsEngineer"),
        ("05-evaluation-engineer", "EvaluationEngineer"),
    ]

    for file_name, class_name in agent_modules:
        py_file = eng_roles_dir / f"{file_name}.py"
        try:
            loader = importlib.machinery.SourceFileLoader(
                file_name.replace("-", "_"), str(py_file))
            mod = loader.load_module()
            cls = getattr(mod, class_name)
            instance = cls(biz_project_id="1.1-pmo-self")
            print(f"  ✅ {class_name} 可实例化 (stage={instance.stage})")
            passed += 1
        except Exception as e:
            print(f"  ❌ {class_name} 实例化失败: {e}")
            failed += 1

    # Check register.yaml
    reg = eng_roles_dir / "register.yaml"
    if reg.exists():
        content = reg.read_text()
        if "0.0.13" in content:
            print(f"  ✅ register.yaml 引用 0.0.13")
            passed += 1
        else:
            print(f"  ⚠️ register.yaml 未引用 0.0.13")
            failed += 1
    else:
        print(f"  ❌ register.yaml 缺失")
        failed += 1

    print(f"\n  G3 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def main():
    print("=" * 60)
    print("m2.3 业务 agent + 5 阶段研发角色骨架 自测")
    print(f"PMO_ROOT: {PMO_ROOT}")
    print("=" * 60)

    g1_pass, g1_p, g1_f = test_g1_5stage_templates()
    g2_pass, g2_p, g2_f = test_g2_biz_agents_framework()
    g3_pass, g3_p, g3_f = test_g3_5stage_activation()

    total_pass = g1_p + g2_p + g3_p
    total_fail = g1_f + g2_f + g3_f
    total = total_pass + total_fail

    print("\n" + "=" * 60)
    print(f"m2.3 自测结果: {total_pass}/{total} 通过")
    print(f"  G1 (5 阶段 agent 模板): {g1_p}/{g1_p+g1_f} ✅" if g1_pass else f"  G1: {g1_p}/{g1_p+g1_f} ❌")
    print(f"  G2 (biz-agents 框架): {g2_p}/{g2_p+g2_f} ✅" if g2_pass else f"  G2: {g2_p}/{g2_p+g2_f} ❌")
    print(f"  G3 (5 阶段 agent 激活): {g3_p}/{g3_p+g3_f} ✅" if g3_pass else f"  G3: {g3_p}/{g3_p+g3_f} ❌")
    print("=" * 60)

    # Write report
    import json
    report = {
        "task": "m2.3",
        "version": "v0.14.0",
        "timestamp": "2026-06-19T12:57:00+08:00",
        "total_tests": total,
        "passed": total_pass,
        "failed": total_fail,
        "tests": [
            {"name": "G1_5stage_templates", "passed": g1_pass, "count": g1_p + g1_f, "sub_pass": g1_p},
            {"name": "G2_biz_agents_framework", "passed": g2_pass, "count": g2_p + g2_f, "sub_pass": g2_p},
            {"name": "G3_5stage_activation", "passed": g3_pass, "count": g3_p + g3_f, "sub_pass": g3_p},
        ],
        "overall": total_fail == 0,
    }
    report_dir = PMO_ROOT / "tests"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "m2.3-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
    return total_fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
