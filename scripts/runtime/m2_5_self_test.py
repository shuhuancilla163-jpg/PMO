"""
m2_5_self_test.py — m2.5 自测

验收点:
- J1: PMO↔业务契约可查 (3 份契约模板)
- J2: 业务对外接口留接口 (contract-biz-external-interface.md)
- J3: 项目间消息契约 (m1.6 已覆盖, 验证 Message-Broker-Agent)
"""

import os
from pathlib import Path

PMO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_j1_pmo_biz_contracts():
    """J1: PMO↔业务契约可查"""
    print("\n=== J1: PMO↔业务契约 ===")
    passed = 0
    failed = 0

    templates_dir = PMO_ROOT / "biz-projects" / "templates"
    contracts = [
        "contract-project-overall.md",
        "contract-eng-5-stages.md",
        "contract-biz-ops-roles.md",
    ]
    for c in contracts:
        p = templates_dir / c
        if p.exists() and p.stat().st_size > 500:
            print(f"  ✅ {c} ({p.stat().st_size} bytes)")
            passed += 1
        else:
            print(f"  ❌ {c} 缺失或太小")
            failed += 1

    print(f"\n  J1 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_j2_biz_external_interface():
    """J2: 业务对外接口留接口"""
    print("\n=== J2: 业务对外接口留接口 ===")
    passed = 0
    failed = 0

    p = PMO_ROOT / "biz-projects" / "templates" / "contract-biz-external-interface.md"
    if p.exists() and p.stat().st_size > 500:
        print(f"  ✅ contract-biz-external-interface.md ({p.stat().st_size} bytes)")
        passed += 1
    else:
        print(f"  ❌ contract-biz-external-interface.md 缺失或太小")
        failed += 1
        return failed == 0, passed, failed

    content = p.read_text()
    checks = [
        ("接口列表", ["接口编号", "接口名称"]),
        ("接口详情", ["方向", "协议", "端点"]),
        ("PMO 监管边界", ["PMO 监管"]),
        ("框架态说明", ["框架态"]),
    ]
    for name, keywords in checks:
        if all(kw in content for kw in keywords):
            print(f"  ✅ {name} 字段存在")
            passed += 1
        else:
            print(f"  ❌ {name} 字段缺失")
            failed += 1

    print(f"\n  J2 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_j3_message_broker():
    """J3: 项目间消息契约 (m1.6 已覆盖)"""
    print("\n=== J3: 项目间消息契约 (m1.6 已覆盖) ===")

    msg_broker = PMO_ROOT / "scripts" / "runtime" / "protocol" / "message_broker.py"
    msg_docs = PMO_ROOT / "docs" / "m1.6-message-broker.md"

    if msg_broker.exists() and msg_docs.exists():
        print(f"  ✅ Message-Broker-Agent 实现存在 ({msg_broker.stat().st_size} bytes)")
        print(f"  ✅ m1.6 文档存在 ({msg_docs.stat().st_size} bytes)")
        print(f"  ✅ J3 由 m1.6 覆盖 (D17 自检已验证)")
        print(f"\n  J3 结果: 1/1 通过 (m1.6 覆盖)")
        return True, 1, 0
    else:
        print(f"  ❌ Message-Broker-Agent ({msg_broker.exists()}) 或 m1.6 文档 ({msg_docs.exists()}) 缺失")
        print(f"\n  J3 结果: 0/1 失败")
        return False, 0, 1


def main():
    print("=" * 60)
    print("m2.5 跨边界契约骨架 自测")
    print(f"PMO_ROOT: {PMO_ROOT}")
    print("=" * 60)

    j1_pass, j1_p, j1_f = test_j1_pmo_biz_contracts()
    j2_pass, j2_p, j2_f = test_j2_biz_external_interface()
    j3_pass, j3_p, j3_f = test_j3_message_broker()

    total_pass = j1_p + j2_p + j3_p
    total_fail = j1_f + j2_f + j3_f
    total = total_pass + total_fail

    print("\n" + "=" * 60)
    print(f"m2.5 自测结果: {total_pass}/{total} 通过")
    print(f"  J1 (PMO↔业务契约): {j1_p}/{j1_p+j1_f} {'✅' if j1_pass else '❌'}")
    print(f"  J2 (业务对外接口): {j2_p}/{j2_p+j2_f} {'✅' if j2_pass else '❌'}")
    print(f"  J3 (项目间消息契约): {j3_p}/{j3_p+j3_f} {'✅' if j3_pass else '❌'} (m1.6覆盖)")
    print("=" * 60)

    import json
    report = {
        "task": "m2.5",
        "version": "v0.14.0",
        "timestamp": "2026-06-19T13:05:00+08:00",
        "total_tests": total,
        "passed": total_pass,
        "failed": total_fail,
        "tests": [
            {"name": "J1_pmo_biz_contracts", "passed": j1_pass, "count": j1_p + j1_f, "sub_pass": j1_p},
            {"name": "J2_biz_external_interface", "passed": j2_pass, "count": j2_p + j2_f, "sub_pass": j2_p},
            {"name": "J3_message_broker_m16", "passed": j3_pass, "count": j3_p + j3_f, "sub_pass": j3_p},
        ],
        "overall": total_fail == 0,
    }
    report_dir = PMO_ROOT / "tests"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / "m2.5-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
    return total_fail == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
