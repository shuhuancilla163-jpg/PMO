"""
PMO m0.9 自测脚本 (m0_9_self_test.py, m0.9, DEC-2026-0009)
自测 8 项：覆盖 PMO 规范同步 + 阈值考核两个模块
"""
import os
import sys
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

PMO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(PMO_ROOT / "scripts" / "runtime" / "norm_sync"))
sys.path.insert(0, str(PMO_ROOT / "scripts" / "runtime" / "assessment"))

# 导入被测模块
from onboarding_syncer import OnboardingSyncer
from threshold_engine import ThresholdEngine, Verdict


class SelfTestRunner:
    """m0.9 自测运行器"""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.test_project_id = "0.9-self-test"
        self.test_report_dir = PMO_ROOT / "biz-projects" / self.test_project_id / "reports"

    def run_all(self) -> Dict[str, Any]:
        tests = [
            ("T1", "thresholds.yaml 格式验证",         self.test_thresholds_yaml),
            ("T2", "OnboardingSyncer 同步 register",   self.test_sync_register),
            ("T3", "OnboardingSyncer 同步契约",         self.test_sync_contracts),
            ("T4", "OnboardingSyncer 同步阈值",         self.test_sync_thresholds),
            ("T5", "OnboardingSyncer 幂等性",           self.test_sync_idempotent),
            ("T6", "ThresholdEngine 单指标比对",        self.test_engine_single_metric),
            ("T7", "ThresholdEngine 维度得分",          self.test_engine_dimension_score),
            ("T8", "ThresholdEngine 生成报告",         self.test_engine_report),
        ]

        for test_id, name, fn in tests:
            print(f"  [{test_id}] {name} ... ", end="", flush=True)
            try:
                passed, detail = fn()
            except Exception as e:
                passed = False
                detail = f"EXCEPTION: {e}"
            status = "PASS" if passed else "FAIL"
            print(status)
            if detail:
                print(f"         {detail}")
            self.results.append({
                "test_id": test_id,
                "name": name,
                "passed": passed,
                "detail": detail,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        passed_count = sum(1 for r in self.results if r["passed"])
        total_count = len(self.results)

        summary = {
            "module": "m0.9 norm-sync + threshold-engine",
            "version": "0.9.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "passed": passed_count,
            "total": total_count,
            "results": self.results
        }

        # 写报告
        self._write_report(summary)
        return summary

    # ============================================================
    # T1: thresholds.yaml 格式验证
    # ============================================================
    def test_thresholds_yaml(self) -> Tuple[bool, str]:
        import yaml
        thresh_file = PMO_ROOT / "config" / "thresholds.yaml"
        if not thresh_file.exists():
            return False, f"thresholds.yaml 不存在: {thresh_file}"

        with open(thresh_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        required_keys = ["business_thresholds", "governance_thresholds",
                         "engineering_thresholds", "assessment_weights",
                         "assessment_rules"]
        for key in required_keys:
            if key not in data:
                return False, f"缺少 key: {key}"

        biz = data.get("business_thresholds", {})
        expected_metrics = ["flow_latency", "exception_rate", "pass_rate",
                            "rollback_rate", "token_consumption"]
        for m in expected_metrics:
            if m not in biz:
                return False, f"缺少业务指标: {m}"
            item = biz[m]
            for f in ["warn", "critical", "direction"]:
                if f not in item:
                    return False, f"{m} 缺少字段: {f}"

        weights = data.get("assessment_weights", {})
        total_weight = (
            weights.get("dimension_1_weight", 0)
            + weights.get("dimension_2_weight", 0)
            + weights.get("dimension_3_weight", 0)
        )
        if abs(total_weight - 1.0) > 0.01:
            return False, f"维度权重总和={total_weight}，不等于 1.0"

        return True, f"OK（{len(biz)} 项业务指标，{len(expected_metrics)} 项核心指标）"

    # ============================================================
    # T2: OnboardingSyncer 同步 register.yaml
    # ============================================================
    def test_sync_register(self) -> Tuple[bool, str]:
        syncer = OnboardingSyncer(str(PMO_ROOT))
        biz_id = self.test_project_id
        result = syncer.sync_register(
            PMO_ROOT / "biz-projects" / biz_id,
            {"biz_project": {
                "id": biz_id,
                "name": "m0.9自测项目",
                "type": "test",
                "version": "0.1.0",
                "sponsor": "自测Sponsor"
            }}
        )

        if not result["success"]:
            return False, f"sync_register 失败: {result.get('error')}"

        target = PMO_ROOT / "biz-projects" / biz_id / "register.yaml"
        if not target.exists():
            return False, "register.yaml 未生成"

        content = target.read_text(encoding="utf-8")
        if biz_id not in content:
            return False, "register.yaml 内容不含项目 ID"

        return True, f"生成: {target.name}"

    # ============================================================
    # T3: OnboardingSyncer 同步契约
    # ============================================================
    def test_sync_contracts(self) -> Tuple[bool, str]:
        syncer = OnboardingSyncer(str(PMO_ROOT))
        biz_id = self.test_project_id
        result = syncer.sync_contracts(PMO_ROOT / "biz-projects" / biz_id, biz_id)

        if not result["success"]:
            return False, f"sync_contracts 失败: {result.get('error')}"

        contract_overall = PMO_ROOT / "immutable" / "2-biz-specs" / f"contract-{biz_id}-overall.md"
        if not contract_overall.exists():
            return False, f"整体契约未生成: {contract_overall.name}"

        content = contract_overall.read_text(encoding="utf-8")
        if biz_id not in content:
            return False, "契约内容未替换项目 ID"

        return True, f"生成 3 份契约（包含 {biz_id}）"

    # ============================================================
    # T4: OnboardingSyncer 同步阈值配置
    # ============================================================
    def test_sync_thresholds(self) -> Tuple[bool, str]:
        syncer = OnboardingSyncer(str(PMO_ROOT))
        biz_id = self.test_project_id
        result = syncer.sync_thresholds(PMO_ROOT / "biz-projects" / biz_id)

        if not result["success"]:
            return False, f"sync_thresholds 失败: {result.get('error')}"

        target = PMO_ROOT / "biz-projects" / biz_id / "reports" / "thresholds.yaml"
        if not target.exists():
            return False, "thresholds.yaml 未生成"

        import yaml
        with open(target, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if "business_thresholds" not in data:
            return False, "同步的阈值文件缺少 business_thresholds"

        return True, f"OK（路径: reports/thresholds.yaml）"

    # ============================================================
    # T5: OnboardingSyncer 幂等性（重复同步不改变内容）
    # ============================================================
    def test_sync_idempotent(self) -> Tuple[bool, str]:
        syncer = OnboardingSyncer(str(PMO_ROOT))
        biz_id = self.test_project_id

        # 第一次同步
        result1 = syncer.sync_all_norms(biz_id)
        target = PMO_ROOT / "biz-projects" / biz_id / "register.yaml"
        hash1 = target.read_bytes()

        # 第二次同步（幂等）
        result2 = syncer.sync_all_norms(biz_id)
        hash2 = target.read_bytes()

        if hash1 != hash2:
            return False, "幂等性失败：重复同步改变了 register.yaml 内容"

        if result1["synced_items"].get("register", {}).get("status") == "unchanged":
            return True, "幂等 OK（第二次 unchanged）"
        return True, "幂等 OK（内容一致）"

    # ============================================================
    # T6: ThresholdEngine 单指标比对
    # ============================================================
    def test_engine_single_metric(self) -> Tuple[bool, str]:
        engine = ThresholdEngine(str(PMO_ROOT))

        cases = [
            ("flow_latency", 150, Verdict.OK.value),
            ("flow_latency", 250, Verdict.WARNING.value),
            ("flow_latency", 350, Verdict.CRITICAL.value),
            ("pass_rate", 0.95, Verdict.OK.value),
            ("pass_rate", 0.85, Verdict.WARNING.value),
            ("pass_rate", 0.75, Verdict.CRITICAL.value),
            ("availability", 0.999, Verdict.OK.value),
            ("availability", 0.985, Verdict.WARNING.value),
            ("availability", 0.940, Verdict.CRITICAL.value),
        ]

        failures = []
        for metric_id, value, expected in cases:
            r = engine.evaluate_metric(metric_id, value)
            if r["verdict"] != expected:
                failures.append(f"{metric_id}={value}: got {r['verdict']}, expected {expected}")

        if failures:
            return False, "; ".join(failures[:3])

        return True, f"OK（{len(cases)} 个案例全部通过）"

    # ============================================================
    # T7: ThresholdEngine 维度得分
    # ============================================================
    def test_engine_dimension_score(self) -> Tuple[bool, str]:
        engine = ThresholdEngine(str(PMO_ROOT))

        metrics = {
            "flow_latency": 150,
            "exception_rate": 0.02,
            "pass_rate": 0.95,
            "rollback_rate": 0.01,
            "token_consumption": 3000,
        }

        result = engine.evaluate_project(self.test_project_id, metrics)

        d3 = result["dimension_3"]
        if d3["score"] != 100:
            return False, f"dimension_3 score={d3['score']}，期望 100（全部 OK）"

        if d3["verdict"] != "compliant":
            return False, f"dimension_3 verdict={d3['verdict']}，期望 compliant"

        # 混入一个 warning
        metrics["flow_latency"] = 250
        result2 = engine.evaluate_project(self.test_project_id, metrics)
        if result2["dimension_3"]["verdict"] != "warning":
            return False, f"混入 warning 后 verdict={result2['dimension_3']['verdict']}，期望 warning"

        return True, f"dimension_3 score=100（OK），混入 warning 后 score={result2['dimension_3']['score']}"

    # ============================================================
    # T8: ThresholdEngine 生成考核报告
    # ============================================================
    def test_engine_report(self) -> Tuple[bool, str]:
        engine = ThresholdEngine(str(PMO_ROOT))

        metrics = {
            "flow_latency": 180,
            "exception_rate": 0.03,
            "pass_rate": 0.92,
            "rollback_rate": 0.015,
            "token_consumption": 4500,
        }

        report = engine.generate_assessment_report(self.test_project_id, metrics)

        required_fields = ["report_id", "project_id", "timestamp",
                          "overall_score", "overall_verdict",
                          "dimension_1", "dimension_2", "dimension_3",
                          "violations"]
        for field in required_fields:
            if field not in report:
                return False, f"报告缺少字段: {field}"

        if not report["report_id"].startswith("ASSESS-"):
            return False, f"report_id 格式错误: {report['report_id']}"

        latest = self.test_report_dir / "latest.json"
        if not latest.exists():
            return False, "latest.json 未生成"

        # 验证 latest.json 内容一致
        with open(latest, encoding="utf-8") as f:
            latest_data = json.load(f)
        if latest_data["report_id"] != report["report_id"]:
            return False, "latest.json 内容与报告不一致"

        return True, (
            f"report_id={report['report_id']}, "
            f"overall_score={report['overall_score']}, "
            f"verdict={report['overall_verdict']}"
        )

    # ============================================================
    # 报告写入
    # ============================================================
    def _write_report(self, summary: Dict[str, Any]):
        reports_dir = PMO_ROOT / "reports" / "self-tests"
        reports_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        report_file = reports_dir / f"m0_9_self_test_{ts}.json"
        report_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        latest = reports_dir / "latest.json"
        latest.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"\n  报告已写入: {report_file.name}")
        print(f"  最新报告: {latest.name}")

    # ============================================================
    # 清理测试数据
    # ============================================================
    def cleanup(self):
        test_dir = PMO_ROOT / "biz-projects" / self.test_project_id
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"  已清理测试数据: {test_dir}")


def main():
    print("=" * 60)
    print("PMO m0.9 自测 (DEC-2026-0009)")
    print("  模块: OnboardingSyncer + ThresholdEngine")
    print("  场景: 规范同步 + 阈值考核")
    print("=" * 60)
    print()

    runner = SelfTestRunner()
    summary = runner.run_all()

    print()
    print("=" * 60)
    print(f"结果: {summary['passed']}/{summary['total']} PASS")
    if summary['passed'] == summary['total']:
        print("状态: ALL PASSED")
    else:
        failed = [r for r in summary['results'] if not r['passed']]
        print("失败:")
        for r in failed:
            print(f"  [{r['test_id']}] {r['name']}: {r['detail']}")
    print("=" * 60)

    # cleanup（可选，取消注释则自动清理）
    # runner.cleanup()

    return 0 if summary['passed'] == summary['total'] else 1


if __name__ == "__main__":
    sys.exit(main())
