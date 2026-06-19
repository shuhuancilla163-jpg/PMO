"""
m2.1 业务元数据 3 项自测 (m2_1_self_test.py, DEC-2026-0005)
- 3 项验收点 (按 plan):
  1. 业务元数据 3 项可建 (E1 业务项目元数据)
  2. 业务数据 schema 可定义 (E2, 业务项目定义, PMO 存)
  3. 业务术语表可建 (E3, 业务 agent 定义, PMO 验证)
- 验证项: E1 必填字段 + E2 schema 验证 + E3 术语表验证 + 业务 agent role 边界
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 注: 不能直接 from biz_metadata import ... 因为模块名是 biz_metadata.py
# 改用 importlib 直接加载
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "biz_metadata_mod",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "biz_metadata.py")
)
_biz_metadata = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_biz_metadata)
BizMetadataStore = _biz_metadata.BizMetadataStore
ENG_5_STAGES_ROLES = _biz_metadata.ENG_5_STAGES_ROLES


PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def run_m2_1_self_test() -> dict:
    """跑 m2.1 3 项验收, 返回报告"""
    print("=" * 60)
    print("m2.1 业务元数据 3 项自测 (DEC-2026-0005)")
    print("=" * 60 + "\n")
    store = BizMetadataStore(PMO_ROOT)
    results = []

    # ============================================
    # 验收 1: E1 业务项目元数据可建
    # ============================================
    print("[1/3] 验收 1: E1 业务项目元数据可建 (biz_project 必填字段)")
    e1_1 = store.load_e1("1.1-pmo-self")
    e1_2 = store.load_e1("1.2-finance")
    e1_1_ok = e1_1.get("success", False)
    e1_2_ok = e1_2.get("success", False)
    e1_1_bp = e1_1.get("e1", {}).get("biz_project", {}) if e1_1_ok else {}
    e1_2_bp = e1_2.get("e1", {}).get("biz_project", {}) if e1_2_ok else {}
    fields_ok = all([
        e1_1_bp.get("id"), e1_1_bp.get("name"), e1_1_bp.get("type"),
        e1_1_bp.get("version"), e1_1_bp.get("sponsor"), e1_1_bp.get("registered_at")
    ])
    e1_ok = e1_1_ok and e1_2_ok and fields_ok
    check1 = {
        "id": "V1_e1_metadata_buildable",
        "name": "E1 业务项目元数据可建",
        "result": "pass" if e1_ok else "fail",
        "details": f"1.1={e1_1_bp.get('id', 'FAIL')}({e1_1_bp.get('name', 'FAIL')}), 1.2={e1_2_bp.get('id', 'FAIL')}({e1_2_bp.get('name', 'FAIL')}), 6 必填字段全 OK"
    }
    results.append(check1)
    print(f"  - {check1['result'].upper()}: {check1['details']}\n")

    # ============================================
    # 验收 2: E2 业务数据 schema 可定义
    # ============================================
    print("[2/3] 验收 2: E2 业务数据 schema 可定义 (业务项目定义, PMO 存)")
    e2_1 = store.load_e2("1.1-pmo-self")
    e2_2 = store.load_e2("1.2-finance")
    e2_1_ok = e2_1.get("success", False)
    e2_2_ok = e2_2.get("success", False)
    e2_1_entities = len(e2_1.get("e2", {}).get("biz_data_schema", {}).get("entities", [])) if e2_1_ok else 0
    e2_2_entities = len(e2_2.get("e2", {}).get("biz_data_schema", {}).get("entities", [])) if e2_2_ok else 0
    # 验证 schema 字段
    e2_1_schema = e2_1.get("e2", {}).get("biz_data_schema", {}) if e2_1_ok else {}
    schema_ok = (
        e2_1_schema.get("defined_by") == "biz_project" and
        e2_1_schema.get("stored_by") == "pmo_instance"
    )
    e2_ok = e2_1_ok and e2_2_ok and schema_ok
    check2 = {
        "id": "V2_e2_schema_defineable",
        "name": "E2 业务数据 schema 可定义",
        "result": "pass" if e2_ok else "fail",
        "details": f"1.1={e2_1_entities} 实体, 1.2={e2_2_entities} 实体, defined_by=biz_project/stored_by=pmo_instance 验证 OK"
    }
    results.append(check2)
    print(f"  - {check2['result'].upper()}: {check2['details']}\n")

    # ============================================
    # 验收 3: E3 业务术语表可建 + 业务 agent role 边界
    # ============================================
    print("[3/3] 验收 3: E3 业务术语表可建 (业务 agent 定义, PMO 验证 + role 边界)")
    e3_1 = store.load_e3("1.1-pmo-self")
    e3_2 = store.load_e3("1.2-finance")
    e3_1_ok = e3_1.get("success", False)
    e3_2_ok = e3_2.get("success", False)
    e3_1_terms = len(e3_1.get("e3", {}).get("biz_glossary", {}).get("terms", [])) if e3_1_ok else 0
    e3_2_terms = len(e3_2.get("e3", {}).get("biz_glossary", {}).get("terms", [])) if e3_2_ok else 0
    e3_1_roles = len(e3_1.get("e3", {}).get("biz_glossary", {}).get("roles", [])) if e3_1_ok else 0
    e3_2_roles = len(e3_2.get("e3", {}).get("biz_glossary", {}).get("roles", [])) if e3_2_ok else 0
    # 验证业务 agent role 不与 5 阶段研发 role 重名
    conflict_count = 0
    for pid, e3 in [("1.1-pmo-self", e3_1), ("1.2-finance", e3_2)]:
        if e3.get("success"):
            for role in e3.get("e3", {}).get("biz_glossary", {}).get("roles", []):
                if role.get("role", "") in ENG_5_STAGES_ROLES:
                    conflict_count += 1
    role_boundary_ok = conflict_count == 0
    e3_ok = e3_1_ok and e3_2_ok and role_boundary_ok
    check3 = {
        "id": "V3_e3_glossary_buildable",
        "name": "E3 业务术语表可建",
        "result": "pass" if e3_ok else "fail",
        "details": f"1.1={e3_1_terms} 术语+{e3_1_roles} 角色, 1.2={e3_2_terms} 术语+{e3_2_roles} 角色, role 冲突={conflict_count} (DEC-2026-0003 边界)"
    }
    results.append(check3)
    print(f"  - {check3['result'].upper()}: {check3['details']}\n")

    # ============================================
    # 总评
    # ============================================
    total = len(results)
    passed = sum(1 for r in results if r["result"] == "pass")
    pass_rate = passed / total * 100
    report = {
        "version": "0.12.0",
        "decision": "DEC-2026-0005",
        "test_date": datetime.now(timezone.utc).isoformat(),
        "task": "m2.1 业务元数据 3 项",
        "checks": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{pass_rate:.1f}%"
        },
        "acceptance_criteria": "3 项全部 pass, m2.1 通过",
        "status": "completed" if passed == total else "partial"
    }

    print("=" * 60)
    print(f"m2.1 自测结果: {passed}/{total} pass ({pass_rate:.1f}%)")
    print("=" * 60)
    if passed == total:
        print("✅ m2.1 通过, 准备 v0.12.0 发布 + Sponsor review")
    else:
        print("⚠️ m2.1 部分通过, 需修复")
    return report


if __name__ == "__main__":
    report = run_m2_1_self_test()
    # 写报告
    tests_dir = Path(PMO_ROOT) / "tests"
    tests_dir.mkdir(exist_ok=True)
    report_file = tests_dir / "m2.1-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
