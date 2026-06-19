"""
m0.8 双向消息通知端到端自测 (m0_8_self_test.py, DEC-2026-0008)
验收 5 项子检查:
  N1: Schema Watcher 监听 E2/E3 变更，生成变更事件
  N2: 变更事件写入 logs/schema-watcher/change-events-YYYYMMDD.json
  N3: pmo.schema.change 轻量 Ping 可发（Message-Broker）
  N4: 业务系统上报 metric/exception/data 全通
  N5: ACK 超时告警可触发
"""
import json
import os
import sys
import tempfile
import shutil
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_m0_8_self_test() -> dict:
    print("=" * 60)
    print("m0.8 双向消息通知端到端自测 (DEC-2026-0008)")
    print("=" * 60 + "\n")

    results = []

    # ============================================
    # N1: Schema Watcher 监听变更，生成事件
    # ============================================
    print("[N1] Schema Watcher 监听 E2/E3 变更，生成变更事件")

    from schema_watcher.schema_watcher import SchemaWatcher, ChangeSeverity

    watcher = SchemaWatcher(PMO_ROOT)

    # 创建临时 E2 文件来触发变更检测
    temp_e2_path = Path(PMO_ROOT) / "config" / "biz-meta" / "E2-schema-test.json"
    original_content = {"version": "1.0", "schema": {"type": "object"}}
    temp_e2_path.write_text(json.dumps(original_content), encoding="utf-8")

    # 初始化快照（包含新文件）
    watcher._file_hashes[str(temp_e2_path)] = watcher._sha256(json.dumps(original_content))

    # 修改文件内容触发变更
    new_content = {"version": "1.1", "schema": {"type": "object", "properties": {"x": {"type": "string"}}}}
    temp_e2_path.write_text(json.dumps(new_content), encoding="utf-8")

    events = watcher.check_for_changes()
    n1_ok = any(
        "schema_change" in ev.get("event_type", "")
        and any("E2-schema-test" in f["file"] for f in ev.get("changed_files", []))
        for ev in events
    )
    check1 = {
        "id": "N1_schema_watcher_detects_change",
        "name": "Schema Watcher 监听变更生成事件",
        "result": "pass" if n1_ok else "fail",
        "details": f"变更事件数: {len(events)}, 检测到 E2-schema-test 变更: {n1_ok}"
    }
    results.append(check1)
    print(f"  [{check1['result'].upper()}] {check1['details']}\n")

    # 清理临时文件
    try:
        temp_e2_path.unlink()
    except Exception:
        pass

    # ============================================
    # N2: 变更事件写入事件日志文件
    # ============================================
    print("[N2] 变更事件写入 logs/schema-watcher/change-events-YYYYMMDD.json")

    # 创建临时文件触发第二次变更（验证写入）
    temp_e2_path2 = Path(PMO_ROOT) / "config" / "biz-meta" / "E2-schema-test2.json"
    v1 = {"version": "1.0", "schema": {}}
    v2 = {"version": "1.2", "schema": {"breaking": True}}
    temp_e2_path2.write_text(json.dumps(v1), encoding="utf-8")
    watcher._file_hashes[str(temp_e2_path2)] = watcher._sha256(json.dumps(v1))
    watcher._file_versions[str(temp_e2_path2)] = "1.0"

    temp_e2_path2.write_text(json.dumps(v2), encoding="utf-8")
    watcher._file_versions[str(temp_e2_path2)] = "1.2"

    events2 = watcher.check_for_changes()
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_file = watcher.events_dir / f"change-events-{today}.json"

    n2_ok = log_file.exists() and log_file.stat().st_size > 0
    if n2_ok:
        try:
            log_data = json.loads(log_file.read_text(encoding="utf-8"))
            n2_ok = isinstance(log_data, list) and len(log_data) > 0
        except Exception:
            n2_ok = False

    check2 = {
        "id": "N2_change_event_written_to_log",
        "name": "变更事件写入事件日志",
        "result": "pass" if n2_ok else "fail",
        "details": f"日志文件: {log_file.name}, 存在: {log_file.exists()}, 大小: {log_file.stat().st_size if log_file.exists() else 0} bytes"
    }
    results.append(check2)
    print(f"  [{check2['result'].upper()}] {check2['details']}\n")

    # 清理
    try:
        temp_e2_path2.unlink()
    except Exception:
        pass

    # ============================================
    # N3: pmo.schema.change 轻量 Ping 可发
    # ============================================
    print("[N3] pmo.schema.change 轻量 Ping 可发（Message-Broker）")

    from protocol.message_broker import MessageBroker

    broker = MessageBroker(PMO_ROOT)
    watcher._broker = broker  # 复用实例

    # 手动发一个 Ping（不触发文件变更）
    test_event = {
        "event_id": "EVT-TEST-001",
        "event_type": "schema_change",
        "changed_files": [{"file": "E2-schema-test.json", "old_hash": "abc", "new_hash": "def", "old_version": "1.0", "new_version": "1.1", "changed_at": datetime.now(timezone.utc).isoformat()}],
        "affected_biz_projects": ["1.2-finance"],
        "severity": "info",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # 直接发 ping
    try:
        msg = broker.publish(
            from_project="pmo-schema-watcher",
            to_project="biz-system",
            topic="pmo.schema.change",
            msg_type="notification",
            content={
                "event_id": test_event["event_id"],
                "event_type": test_event["event_type"],
                "changed_files_summary": ["E2-schema-test.json"],
                "severity": "info",
                "pmo_instance": "PMO-L1",
                "timestamp": test_event["timestamp"],
                "affected_biz_projects": ["1.2-finance"],
                "pull_url": f"/pmo-api/v1/schema/changes/{test_event['event_id']}"
            },
            qos="1",
            layer="pmo"
        )
        n3_ok = msg.status.value in ("delivered", "acked", "pending")
        # 验证 payload 不含完整内容（轻量）
        msg_content = msg.content
        has_full_diff = "diff" in msg_content or "full_content" in msg_content
        n3_ok = n3_ok and not has_full_diff
    except Exception as e:
        n3_ok = False

    check3 = {
        "id": "N3_schema_change_ping_sent",
        "name": "pmo.schema.change 轻量 Ping 可发",
        "result": "pass" if n3_ok else "fail",
        "details": f"pmo.schema.change Ping 已发, 不含完整 diff 内容"
    }
    results.append(check3)
    print(f"  [{check3['result'].upper()}] {check3['details']}\n")

    # ============================================
    # N4: 业务系统上报 metric/exception/data 全通
    # ============================================
    print("[N4] 业务系统上报 metric/exception/data 全通")

    n4_checks = {}

    # 4a: metric 上报
    r_metric = watcher.handle_biz_report(
        biz_project_id="1.2-finance",
        report_type="metric",
        payload={
            "phase": "P2-develop",
            "metrics": {"flow_latency": 120, "exception_rate": 0.02},
            "period": "5min"
        }
    )
    n4_checks["metric"] = r_metric.get("success", False) and r_metric.get("topic") == "biz.1.2-finance.metric"

    # 4b: exception 上报
    r_exc = watcher.handle_biz_report(
        biz_project_id="1.2-finance",
        report_type="exception",
        payload={
            "exception_type": "VALIDATION_ERROR",
            "exception_code": "E2001",
            "severity": "warning"
        }
    )
    n4_checks["exception"] = r_exc.get("success", False) and r_exc.get("topic") == "biz.1.2-finance.exception"

    # 4c: data 上报
    r_data = watcher.handle_biz_report(
        biz_project_id="1.2-finance",
        report_type="data",
        payload={
            "data_type": "position_snapshot",
            "data_key": "POS-001",
            "data_hash": "sha256:test"
        }
    )
    n4_checks["data"] = r_data.get("success", False) and r_data.get("topic") == "biz.1.2-finance.data"

    n4_ok = all(n4_checks.values())
    check4 = {
        "id": "N4_biz_reports_all_3_types",
        "name": "业务系统上报 metric/exception/data 全通",
        "result": "pass" if n4_ok else "fail",
        "details": f"metric={'OK' if n4_checks['metric'] else 'FAIL'}, exception={'OK' if n4_checks['exception'] else 'FAIL'}, data={'OK' if n4_checks['data'] else 'FAIL'}",
        "sub_checks": {k: "pass" if v else "fail" for k, v in n4_checks.items()}
    }
    results.append(check4)
    print(f"  [{check4['result'].upper()}] {check4['details']}\n")

    # ============================================
    # N5: ACK 超时告警可触发
    # ============================================
    print("[N5] ACK 超时告警可触发")

    # 模拟一个已超时的待 ACK 事件
    past_deadline = datetime.now(timezone.utc) - timedelta(days=8)
    watcher._pending_acks["EVT-TEST-TIMEOUT"] = {
        "event": {
            "event_id": "EVT-TEST-TIMEOUT",
            "affected_biz_projects": ["1.2-finance", "1.3-hedge-fund"],
            "severity": "info"
        },
        "deadline": past_deadline.isoformat(),
        "acks": {},  # 没有 ACK
        "sent": (past_deadline - timedelta(days=1)).isoformat()
    }

    alerts = watcher.check_ack_timeouts()
    n5_ok = any(
        a["event_id"] == "EVT-TEST-TIMEOUT"
        and "1.2-finance" in a["missing_projects"]
        and a["severity"] == "warning"
        for a in alerts
    )
    check5 = {
        "id": "N5_ack_timeout_alert",
        "name": "ACK 超时告警可触发",
        "result": "pass" if n5_ok else "fail",
        "details": f"超时事件数: {len(alerts)}, 触发告警: {n5_ok}"
    }
    results.append(check5)
    print(f"  [{check5['result'].upper()}] {check5['details']}\n")

    # ============================================
    # 总评
    # ============================================
    total = len(results)
    passed = sum(1 for r in results if r["result"] == "pass")
    pass_rate = passed / total * 100

    print("=" * 60)
    print(f"m0.8 自测结果: {passed}/{total} pass ({pass_rate:.1f}%)")
    print("=" * 60)
    if passed == total:
        print("m0.8 通过, 准备提交 DEC-2026-0008 审批")
    else:
        failed = [r["id"] for r in results if r["result"] == "fail"]
        print(f"m0.8 未全过, 失败项: {failed}")
    print()

    report = {
        "version": "0.8.0",
        "decision": "DEC-2026-0008",
        "test_date": datetime.now(timezone.utc).isoformat(),
        "task": "m0.8 双向消息通知",
        "checks": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{pass_rate:.1f}%"
        },
        "acceptance_criteria": "N1-N5 全部 pass, m0.8 通过",
        "status": "completed" if passed == total else "partial"
    }
    return report


if __name__ == "__main__":
    report = run_m0_8_self_test()

    # 写报告
    tests_dir = Path(PMO_ROOT) / "tests"
    tests_dir.mkdir(exist_ok=True)
    report_file = tests_dir / "m0.8-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"报告已写入: {report_file}")
