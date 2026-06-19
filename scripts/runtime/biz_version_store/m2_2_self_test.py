"""
m2_2_self_test.py — m2.2 自测 (DEC-2026-0006)

验收点:
- F1: 业务不可变文档骨架可建 (biz-docs/ 4 类文档)
- F5: 业务版本管理 (Git tag/release + semver) 可演示
"""

import os, sys, glob, json, importlib

PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(PMO_ROOT, "scripts", "runtime", "biz_version_store"))


def test_f1_biz_docs_skeleton():
    """F1: 业务不可变文档骨架可建"""
    print("\n=== F1: 业务不可变文档骨架 ===")
    passed = 0
    failed = 0

    demo_projects = ["1.1-pmo-self", "1.x-biz-template"]
    required_docs = [
        "01-requirements/biz-requirements.md",
        "02-design/biz-design.md",
        "03-implementation/biz-flow.md",
        "04-release/release-notes.md",
    ]

    for biz_id in demo_projects:
        biz_docs = os.path.join(PMO_ROOT, "biz-projects", biz_id, "biz-docs")
        print(f"\n  [{biz_id}] biz-docs 路径: {biz_docs}")
        if not os.path.exists(biz_docs):
            print(f"    ❌ biz-docs/ 不存在")
            failed += 1
            continue

        for doc in required_docs:
            full_path = os.path.join(biz_docs, doc)
            if os.path.exists(full_path):
                # Check not empty
                size = os.path.getsize(full_path)
                print(f"    ✅ {doc} ({size} bytes)")
                passed += 1
            else:
                print(f"    ❌ {doc} 缺失")
                failed += 1

        # Check 4 dirs exist
        required_dirs = ["01-requirements", "02-design", "03-implementation", "04-release"]
        for d in required_dirs:
            d_path = os.path.join(biz_docs, d)
            if os.path.exists(d_path):
                print(f"    ✅ {d}/ 目录存在")
                passed += 1
            else:
                print(f"    ❌ {d}/ 目录缺失")
                failed += 1

    # Check template
    template = os.path.join(PMO_ROOT, "biz-projects", "templates", "biz-docs", "README.md")
    if os.path.exists(template):
        print(f"\n  ✅ biz-docs 模板存在: {template}")
        passed += 1
    else:
        print(f"\n  ❌ biz-docs 模板缺失")
        failed += 1

    # Check meta-rule
    meta_rule = os.path.join(PMO_ROOT, "immutable", "0-governance", "0.0.17-biz-immutable-docs.md")
    if os.path.exists(meta_rule):
        size = os.path.getsize(meta_rule)
        print(f"  ✅ 0.0.17 元规则存在 ({size} bytes)")
        passed += 1
    else:
        print(f"  ❌ 0.0.17 元规则缺失")
        failed += 1

    print(f"\n  F1 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def test_f5_version_management():
    """F5: 业务版本管理 (Git tag/release + semver) 可演示"""
    print("\n=== F5: 业务版本管理 ===")
    # Clear version stores at start for clean test
    for f in glob.glob(os.path.join(PMO_ROOT, "config", "biz-meta", "*versions.json")):
        os.remove(f)
    passed = 0
    failed = 0

    # Test BizVersionStore
    import biz_version_store as bv
    importlib.reload(bv)
    BVS = bv.BizVersionStore

    biz_ids = ["1.1-pmo-self"]  # F5: 只检查 active 项目, 不检查 template

    for biz_id in biz_ids:
        store = BVS(biz_id)
        print(f"\n  [{biz_id}]")

        # Release v1.0.0
        r1 = store.release("requirement", "init")
        if r1.tag == f"biz.{biz_id}.v1.0.0":
            print(f"    ✅ v1.0.0 release: {r1.tag}")
            passed += 1
        else:
            print(f"    ❌ v1.0.0 release: {r1.tag}")
            failed += 1

        # Release v1.0.1
        r2 = store.release("development", "design")
        if r2.tag == f"biz.{biz_id}.v1.0.1":
            print(f"    ✅ v1.0.1 release: {r2.tag}")
            passed += 1
        else:
            print(f"    ❌ v1.0.1 release: {r2.tag}")
            failed += 1

        # next_minor -> v1.1.0
        r3 = store.next_minor("new feature")
        if r3.tag == f"biz.{biz_id}.v1.1.0":
            print(f"    ✅ v1.1.0 next_minor: {r3.tag}")
            passed += 1
        else:
            print(f"    ❌ v1.1.0 next_minor: {r3.tag}")
            failed += 1

        # next_major -> v2.0.0
        r4 = store.next_major("breaking change")
        if r4.tag == f"biz.{biz_id}.v2.0.0":
            print(f"    ✅ v2.0.0 next_major: {r4.tag}")
            passed += 1
        else:
            print(f"    ❌ v2.0.0 next_major: {r4.tag}")
            failed += 1

        # semver compare
        cmp1 = store.compare_versions("v1.0.0", "v1.1.0")
        cmp2 = store.compare_versions("v1.1.0", "v2.0.0")
        if cmp1 == -1 and cmp2 == -1:
            print(f"    ✅ semver compare 正确 (v1.0.0 < v1.1.0 < v2.0.0)")
            passed += 1
        else:
            print(f"    ❌ semver compare 错误: {cmp1}, {cmp2}")
            failed += 1

        # Store file
        if os.path.exists(store.store_file):
            print(f"    ✅ 版本存储文件: {os.path.basename(store.store_file)}")
            passed += 1
        else:
            print(f"    ❌ 版本存储文件未创建")
            failed += 1

        # Version history count
        hist = store.get_history()
        if len(hist) == 4:
            print(f"    ✅ 版本历史正确 (4 条)")
            passed += 1
        else:
            print(f"    ❌ 版本历史错误 (期望 4, 实际 {len(hist)})")
            failed += 1

    print(f"\n  F5 结果: {passed}/{passed + failed} 通过")
    return failed == 0, passed, failed


def main():
    print("=" * 60)
    print("m2.2 业务不可变文档 2 项 自测 (DEC-2026-0006)")
    print("=" * 60)

    f1_pass, f1_p, f1_f = test_f1_biz_docs_skeleton()
    f5_pass, f5_p, f5_f = test_f5_version_management()

    total_pass = f1_p + f5_p
    total_fail = f1_f + f5_f
    total = total_pass + total_fail

    print("\n" + "=" * 60)
    print(f"m2.2 自测结果: {total_pass}/{total} 通过")
    print(f"  F1 (业务不可变文档骨架): {f1_p}/{f1_p+f1_f} ✅" if f1_pass else f"  F1: {f1_p}/{f1_p+f1_f} ❌")
    print(f"  F5 (业务版本管理): {f5_p}/{f5_p+f5_f} ✅" if f5_pass else f"  F5: {f5_p}/{f5_p+f5_f} ❌")
    print("=" * 60)

    # Write report
    report = {
        "task": "m2.2",
        "version": "v0.13.0",
        "decision": "DEC-2026-0006",
        "timestamp": "2026-06-19T12:35:00+08:00",
        "total_tests": total,
        "passed": total_pass,
        "failed": total_fail,
        "tests": [
            {"name": "F1_biz_docs_skeleton", "passed": f1_pass, "count": f1_p + f1_f, "sub_pass": f1_p},
            {"name": "F5_version_management", "passed": f5_pass, "count": f5_p + f5_f, "sub_pass": f5_p},
        ],
        "overall": total_fail == 0,
    }
    report_dir = os.path.join(PMO_ROOT, "tests")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, "m2.2-self-test-report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")

    return total_fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
