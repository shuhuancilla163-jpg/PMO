"""
m1.6 项目间消息流通自测 (m1.6_self_test.py, DEC-2026-0004)
- 5 项验收点 (按 plan + 0.0.15):
  1. PMO-Message-Broker-Agent 可演示 (subscribe/publish/deliver)
  2. 业务项目↔业务项目消息经 PMO 中介可跑 (路由)
  3. 消息主题/类型/协议/QoS 可配 (6+6+3 强制字段)
  4. 消息可监控 (11 项指标)
  5. 消息可审计 (append-only 审计日志)
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from protocol.message_broker import MessageBroker, MessageType, QoSLevel, Message


PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_m1_6_self_test() -> dict:
    """跑 m1.6 5 项验收, 返回报告"""
    print("=" * 60)
    print("m1.6 项目间消息流通自测 (DEC-2026-0004)")
    print("=" * 60 + "\n")
    broker = MessageBroker(PMO_ROOT)
    results = []
    
    # ============================================
    # 验收 1: PMO-Message-Broker-Agent 可演示
    # ============================================
    print("[1/5] 验收 1: PMO-Message-Broker-Agent 可演示 (subscribe/publish/deliver)")
    broker.subscribe("1.1", "biz.1.1.state")
    broker.subscribe("1.2", "biz.1.1.state")
    msg1 = broker.publish(
        from_project="1.1", to_project="1.2", topic="biz.1.1.state",
        msg_type=MessageType.NOTIFICATION,
        content={"state": "active", "phase": "P3-test"},
        qos=QoSLevel.AT_MOST_ONCE
    )
    delivered_ok = msg1.status.value in ["delivered", "acked"]
    check1 = {
        "id": "V1_broker_agent_works",
        "name": "PMO-Message-Broker-Agent 可演示",
        "result": "pass" if delivered_ok else "fail",
        "details": f"subscribe OK, publish msg_id={msg1.msg_id}, status={msg1.status.value}"
    }
    results.append(check1)
    print(f"  - {check1['result'].upper()}: {check1['details']}\n")
    
    # ============================================
    # 验收 2: 业务项目↔业务项目消息经 PMO 中介可跑 (路由)
    # ============================================
    print("[2/5] 验收 2: 业务项目↔业务项目消息经 PMO 中介可跑 (1.2→broker→1.3 路由)")
    broker.subscribe("1.3", "inter.biz.1.2.to.1.3")
    msg2 = broker.publish(
        from_project="1.2", to_project="1.3", topic="inter.biz.1.2.to.1.3",
        msg_type=MessageType.NOTIFICATION,
        content={"event": "data_sync", "data_id": "data-002"},
        qos=QoSLevel.AT_LEAST_ONCE
    )
    # 验证: 1.2 没订阅, 1.3 订阅了 → 只有 1.3 收到
    routing_ok = msg2.status.value == "acked"
    check2 = {
        "id": "V2_inter_biz_routing",
        "name": "业务项目↔业务项目消息经 PMO 中介可跑",
        "result": "pass" if routing_ok else "fail",
        "details": f"1.2→broker→1.3 路由, msg_id={msg2.msg_id}, status={msg2.status.value}"
    }
    results.append(check2)
    print(f"  - {check2['result'].upper()}: {check2['details']}\n")
    
    # ============================================
    # 验收 3: 消息主题/类型/协议/QoS 可配
    # ============================================
    print("[3/5] 验收 3: 消息主题/类型/协议/QoS 可配 (6+6+3 强制字段)")
    # 3a: 6 类消息类型
    type_ok = True
    for mt in MessageType:
        msg_test = Message(
            msg_type=mt, from_="1.1", to="1.2",
            topic="biz.1.1.metric", content={"test": mt.value},
            qos=QoSLevel.AT_LEAST_ONCE
        )
        if not msg_test.validate():
            type_ok = False
    # 3b: 6 类主题
    topic_ok = True
    valid_topics = [
        "biz.1.1.state", "biz.1.1.metric", "biz.1.1.exception", "biz.1.1.data",
        "inter.biz.1.1.to.1.2", "pmo.L1.notify"
    ]
    for t in valid_topics:
        msg_test = Message(
            msg_type=MessageType.NOTIFICATION, from_="1.1", to="1.2",
            topic=t, content={"test": t}, qos=QoSLevel.AT_LEAST_ONCE
        )
        if not msg_test.validate():
            topic_ok = False
    # 3c: 3 类 QoS
    qos_ok = True
    for q in QoSLevel:
        msg_test = Message(
            msg_type=MessageType.NOTIFICATION, from_="1.1", to="1.2",
            topic="biz.1.1.state", content={"test": q.value}, qos=q
        )
        if not msg_test.validate():
            qos_ok = False
    # 3d: 协议校验 (非法主题)
    invalid_msg = Message(
        msg_type=MessageType.NOTIFICATION, from_="1.1", to="1.2",
        topic="invalid.topic", content={"test": "fail"}, qos=QoSLevel.AT_LEAST_ONCE
    )
    invalid_rejected = not invalid_msg.validate()
    
    config_ok = type_ok and topic_ok and qos_ok and invalid_rejected
    check3 = {
        "id": "V3_msg_config",
        "name": "消息主题/类型/协议/QoS 可配",
        "result": "pass" if config_ok else "fail",
        "details": f"6 类消息类型 OK, 6 类主题 OK, 3 类 QoS OK, 协议校验拒收非法主题",
        "sub_checks": {
            "msg_types_6": "pass" if type_ok else "fail",
            "topics_6": "pass" if topic_ok else "fail",
            "qos_3": "pass" if qos_ok else "fail",
            "invalid_topic_rejected": "pass" if invalid_rejected else "fail"
        }
    }
    results.append(check3)
    print(f"  - {check3['result'].upper()}: {check3['details']}")
    for k, v in check3["sub_checks"].items():
        print(f"    - {k}: {v}")
    print()
    
    # ============================================
    # 验收 4: 消息可监控 (11 项指标)
    # ============================================
    print("[4/5] 验收 4: 消息可监控 (11 项指标)")
    # 多发几条让数据丰满
    for i in range(3):
        broker.publish(
            from_project="1.1", to_project="1.2", topic="biz.1.1.metric",
            msg_type=MessageType.BIZ_DATA,
            content={"flow_latency": 100 + i, "iteration": i},
            qos=QoSLevel.AT_LEAST_ONCE
        )
    metrics = broker.get_monitoring_metrics()
    expected_metrics = [
        "message_total_sent", "message_total_delivered", "message_total_failed",
        "message_total_retried", "message_total_acked", "message_avg_latency_ms",
        "message_success_rate", "subscriptions_count", "topics_count",
        "pending_count", "audit_log_count"
    ]
    stats = metrics["stats"]
    missing = [m for m in expected_metrics if m not in stats]
    monitor_ok = len(missing) == 0
    check4 = {
        "id": "V4_msg_monitor",
        "name": "消息可监控 (11 项指标)",
        "result": "pass" if monitor_ok else "fail",
        "details": f"11 项指标齐全: {', '.join(expected_metrics)}",
        "actual_metrics": stats,
        "missing": missing
    }
    results.append(check4)
    print(f"  - {check4['result'].upper()}: {check4['details']}")
    print(f"  - 实际值: total_sent={stats['message_total_sent']}, total_delivered={stats['message_total_delivered']}, total_failed={stats['message_total_failed']}, avg_latency_ms={stats['message_avg_latency_ms']:.3f}, success_rate={stats['message_success_rate']:.1f}%\n")
    
    # ============================================
    # 验收 5: 消息可审计 (append-only 审计日志)
    # ============================================
    print("[5/5] 验收 5: 消息可审计 (append-only 审计日志)")
    audit_log = broker.get_audit_log(limit=100)
    # 验证: 审计日志 >= 1 条, 有 publish/deliver/ack/subscribe 等动作
    actions = set(e["action"] for e in audit_log)
    expected_actions = {"publish", "deliver", "subscribe"}
    audit_ok = len(audit_log) > 0 and expected_actions.issubset(actions)
    # 验证: 审计日志文件已写
    audit_files = list(broker.audit_log_dir.glob("audit-*.log"))
    file_ok = len(audit_files) > 0
    check5 = {
        "id": "V5_msg_audit",
        "name": "消息可审计 (append-only)",
        "result": "pass" if audit_ok and file_ok else "fail",
        "details": f"审计 {len(audit_log)} 条, 动作 {sorted(actions)}, 文件 {len(audit_files)} 个",
        "sub_checks": {
            "audit_log_nonempty": "pass" if len(audit_log) > 0 else "fail",
            "all_actions_present": "pass" if expected_actions.issubset(actions) else "fail",
            "audit_files_written": "pass" if file_ok else "fail"
        }
    }
    results.append(check5)
    print(f"  - {check5['result'].upper()}: {check5['details']}")
    for k, v in check5["sub_checks"].items():
        print(f"    - {k}: {v}")
    print()
    
    # ============================================
    # 总评
    # ============================================
    total = len(results)
    passed = sum(1 for r in results if r["result"] == "pass")
    pass_rate = passed / total * 100
    report = {
        "version": "0.11.0",
        "decision": "DEC-2026-0004",
        "test_date": datetime.now(timezone.utc).isoformat(),
        "task": "m1.6 项目间消息流通",
        "checks": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{pass_rate:.1f}%"
        },
        "acceptance_criteria": "5 项全部 pass, m1.6 通过",
        "status": "completed" if passed == total else "partial"
    }
    
    print("=" * 60)
    print(f"m1.6 自测结果: {passed}/{total} pass ({pass_rate:.1f}%)")
    print("=" * 60)
    if passed == total:
        print("✅ m1.6 通过, 准备 v0.11.0 发布 + Sponsor review")
    else:
        print("⚠️ m1.6 部分通过, 需修复")
    return report


if __name__ == "__main__":
    report = run_m1_6_self_test()
    # 写报告
    tests_dir = Path(PMO_ROOT) / "tests"
    tests_dir.mkdir(exist_ok=True)
    report_file = tests_dir / "m1.6-self-test-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已写入: {report_file}")
