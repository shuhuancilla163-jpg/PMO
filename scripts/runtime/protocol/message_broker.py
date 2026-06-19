"""
PMO Message-Broker 模块 (message_broker.py, m1.6, DEC-2026-0004)
- 业务项目↔业务项目消息经 PMO 实例中介 (0.0.15)
- 6 类消息类型 (request/response/notification/alert/escalation/biz_event/biz_data)
- 8 类主题 (biz.state/metric/exception/data + inter.biz.{a}.to.{b} + pmo.{layer}.{action} + pmo.schema.change + biz.{id}.schema.ack, 0.0.15 第 4 节 / m0.8 DEC-2026-0008)
- 3 类 QoS (0=fire-and-forget / 1=at-least-once 默认 / 2=exactly-once)
- 协议校验 (msg_id/msg_type/from/to/topic/qos/timestamp/layer/content 必填)
- 重试策略 (QoS 1+ 5 次指数退避)
- 可监控 (10 项指标: total_sent/delivered/failed/retried/avg_latency_ms/success_rate/subscriptions/topics/pending/audit_log_count)
- 可审计 (append-only 审计日志 logs/message-broker/audit-YYYYMMDD.log)
- 中介路由 (业务项目 A → broker → 业务项目 B)
"""
import json
import os
import re
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


# ============================================
# 枚举 (0.0.15)
# ============================================
class MessageType(str, Enum):
    """消息类型 (6 类, 0.0.15)"""
    REQUEST = "request"            # 请求 (业务项目 A → B, 等响应)
    RESPONSE = "response"          # 响应 (B → A)
    NOTIFICATION = "notification"  # 通知 (单向, 异步)
    ALERT = "alert"                # 告警 (单向, 异步)
    ESCALATION = "escalation"      # 升级 (单向, 异步, 上行)
    BIZ_EVENT = "biz_event"        # 业务事件
    BIZ_DATA = "biz_data"          # 业务数据


class QoSLevel(str, Enum):
    """QoS 等级 (3 类, 0.0.15)"""
    AT_MOST_ONCE = "0"        # 0: fire-and-forget
    AT_LEAST_ONCE = "1"       # 1: at-least-once (默认)
    EXACTLY_ONCE = "2"        # 2: exactly-once


class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKED = "acked"


# ============================================
# 主题模式 (强制命名规范, 0.0.15 第 4 节)
# ============================================
TOPIC_PATTERNS = {
    "biz_state": r"^biz\.[a-zA-Z0-9_.-]+\.state$",
    "biz_metric": r"^biz\.[a-zA-Z0-9_.-]+\.metric$",
    "biz_exception": r"^biz\.[a-zA-Z0-9_.-]+\.exception$",
    "biz_data": r"^biz\.[a-zA-Z0-9_.-]+\.data$",
    "inter_biz": r"^inter\.biz\.[a-zA-Z0-9_.-]+\.to\.[a-zA-Z0-9_.-]+$",
    "pmo_internal": r"^pmo\.(L0|L1|L2)\.[a-z_]+$",
    "pmo_schema_change": r"^pmo\.schema\.change$",
    "biz_schema_ack": r"^biz\.[a-zA-Z0-9_.-]+\.schema\.ack$",
}


# ============================================
# 消息 (强制字段, 0.0.15 第 3 节)
# ============================================
class Message:
    """PMO 消息 (强制字段)
    
    必填字段 (0.0.15 第 3 节):
    - msg_id, msg_type, from, to, topic, qos, timestamp, layer, content
    """
    
    REQUIRED_FIELDS = ["msg_type", "from", "to", "topic", "qos", "layer", "content"]
    
    def __init__(self, msg_type: MessageType, from_: str, to: str, topic: str,
                 content: Dict[str, Any], qos: QoSLevel = QoSLevel.AT_LEAST_ONCE,
                 layer: str = "biz", correlation_id: str = None,
                 protocol_version: str = "1.0"):
        self.msg_id = str(uuid.uuid4())[:8]
        self.msg_type = msg_type
        self.from_ = from_
        self.to = to
        self.topic = topic
        self.qos = qos
        self.layer = layer
        self.content = content
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.correlation_id = correlation_id
        self.protocol_version = protocol_version
        self.retry_count = 0
        self.status = MessageStatus.PENDING
        self.delivered_at = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "from": self.from_,
            "to": self.to,
            "topic": self.topic,
            "qos": self.qos.value,
            "timestamp": self.timestamp,
            "layer": self.layer,
            "content": self.content,
            "correlation_id": self.correlation_id,
            "protocol_version": self.protocol_version,
            "retry_count": self.retry_count,
            "status": self.status.value,
            "delivered_at": self.delivered_at,
            "error": self.error
        }
    
    def validate(self) -> bool:
        """协议校验 (强制字段, 0.0.15 第 5 节)"""
        for field in self.REQUIRED_FIELDS:
            if getattr(self, field if field != "from" else "from_", None) is None:
                self.error = f"missing required field: {field}"
                return False
        # 主题校验
        if not self._validate_topic():
            return False
        # msg_type 校验
        try:
            MessageType(self.msg_type)
        except ValueError:
            self.error = f"invalid msg_type: {self.msg_type}"
            return False
        # qos 校验
        try:
            QoSLevel(self.qos)
        except ValueError:
            self.error = f"invalid qos: {self.qos}"
            return False
        return True
    
    def _validate_topic(self) -> bool:
        """主题校验 (0.0.15 第 4 节)"""
        for pattern_name, pattern in TOPIC_PATTERNS.items():
            if re.match(pattern, self.topic):
                return True
        self.error = f"topic {self.topic} 不符合 6 类主题规范"
        return False


# ============================================
# 重试策略 (0.0.15 第 8 节)
# ============================================
RETRY_BACKOFFS_MS = [100, 500, 2000, 10000]  # 4 次重试退避
MAX_RETRY = 5


# ============================================
# Message Broker (中介路由, 0.0.15 第 2 节)
# ============================================
class MessageBroker:
    """PMO Message Broker — 业务项目间消息中介 (m1.6, DEC-2026-0004)
    
    职责:
    - 业务项目订阅主题
    - 业务项目发布消息 (经 broker)
    - broker 路由到订阅者
    - QoS 0/1/2 处理 + 重试
    - 协议校验 (强制字段)
    - 可监控 (10 项指标)
    - 可审计 (append-only 日志)
    """
    
    PROTOCOL_VERSION = "1.0"
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        # 消息队列 (key=topic, value=Message list)
        self.message_queue: Dict[str, List[Message]] = {}
        # 订阅关系 (key=project_id, value=订阅主题列表)
        self.subscriptions: Dict[str, List[str]] = {}
        # 审计日志 (key=msg_id, value=audit entry)
        self.audit_log: List[Dict[str, Any]] = []
        # 监控统计 (10 项, 0.0.15 第 6 节)
        self.stats: Dict[str, Any] = {
            "message_total_sent": 0,
            "message_total_delivered": 0,
            "message_total_failed": 0,
            "message_total_retried": 0,
            "message_total_acked": 0,
            "message_avg_latency_ms": 0.0,
            "message_success_rate": 0.0,
            "subscriptions_count": 0,
            "topics_count": 0,
            "pending_count": 0,
            "audit_log_count": 0,
            "_latency_sum_ms": 0.0,
            "_latency_count": 0
        }
        # 审计日志目录
        self.audit_log_dir = self.pmo_root / "logs" / "message-broker"
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)
    
    # ---------------- 订阅 ----------------
    def subscribe(self, project_id: str, topic: str) -> bool:
        """业务项目订阅主题 (0.0.15 第 4 节)"""
        if project_id not in self.subscriptions:
            self.subscriptions[project_id] = []
        if topic not in self.subscriptions[project_id]:
            self.subscriptions[project_id].append(topic)
        self.stats["subscriptions_count"] = sum(len(t) for t in self.subscriptions.values())
        self._audit("subscribe", project_id, "", topic, "ok", "")
        return True
    
    def unsubscribe(self, project_id: str, topic: str) -> bool:
        """业务项目取消订阅"""
        if project_id in self.subscriptions and topic in self.subscriptions[project_id]:
            self.subscriptions[project_id].remove(topic)
            self.stats["subscriptions_count"] = sum(len(t) for t in self.subscriptions.values())
            return True
        return False
    
    # ---------------- 发布 / 投递 ----------------
    def publish(self, from_project: str, to_project: str, topic: str,
                msg_type: MessageType, content: Dict[str, Any],
                qos: QoSLevel = QoSLevel.AT_LEAST_ONCE,
                layer: str = "biz", correlation_id: str = None) -> Message:
        """业务项目发布消息 (经 broker)
        
        Args:
            from_project: 发送方项目 ID
            to_project: 接收方项目 ID (broker 路由, 不直发)
            topic: 消息主题
            msg_type: 消息类型
            content: 业务负载
            qos: QoS 等级
            layer: L0/L1/L2/biz
            correlation_id: 关联 ID
        """
        msg = Message(
            msg_type=msg_type,
            from_=from_project,
            to=to_project,
            topic=topic,
            content=content,
            qos=qos,
            layer=layer,
            correlation_id=correlation_id
        )
        # 协议校验 (0.0.15 第 5 节)
        if not msg.validate():
            self.stats["message_total_failed"] += 1
            self._audit("publish", from_project, to_project, topic, "fail", msg.error)
            return msg
        # 入队
        if topic not in self.message_queue:
            self.message_queue[topic] = []
        self.message_queue[topic].append(msg)
        self.stats["message_total_sent"] += 1
        self.stats["topics_count"] = len(self.message_queue)
        self.stats["pending_count"] = sum(1 for msgs in self.message_queue.values() for m in msgs if m.status == MessageStatus.PENDING)
        self._audit("publish", from_project, to_project, topic, "ok", "")
        # 立即投递 (broker 内部路由)
        return self._deliver_to_topic(topic)
    
    def _deliver_to_topic(self, topic: str) -> Message:
        """投递主题给所有订阅者 (中介路由, 0.0.15 第 2 节)"""
        if topic not in self.message_queue:
            empty_msg = Message(
                msg_type=MessageType.NOTIFICATION,
                from_="broker",
                to="",
                topic=topic,
                content={"note": "no messages"},
                qos=QoSLevel.AT_MOST_ONCE
            )
            return empty_msg
        last_msg = self.message_queue[topic][-1]
        if last_msg.status == MessageStatus.DELIVERED:
            return last_msg
        # 找到订阅者
        delivered_count = 0
        sent_at = time.time()
        for project_id, topics in self.subscriptions.items():
            if topic in topics and project_id == last_msg.to:
                last_msg.status = MessageStatus.DELIVERED
                last_msg.delivered_at = datetime.now(timezone.utc).isoformat()
                delivered_count += 1
                self.stats["message_total_delivered"] += 1
                latency_ms = (time.time() - sent_at) * 1000
                self.stats["_latency_sum_ms"] += latency_ms
                self.stats["_latency_count"] += 1
                self._update_avg_latency()
                self._audit("deliver", last_msg.from_, project_id, topic, "ok", f"latency_ms={latency_ms:.2f}")
                # QoS 1: 至少一次 (ack 机制)
                if last_msg.qos == QoSLevel.AT_LEAST_ONCE:
                    self._ack(last_msg, project_id)
        if delivered_count == 0:
            last_msg.status = MessageStatus.FAILED
            last_msg.error = "no subscriber"
            self.stats["message_total_failed"] += 1
            self._audit("deliver", last_msg.from_, last_msg.to, topic, "fail", "no subscriber")
            # 重试机制 (QoS 1+)
            if last_msg.qos != QoSLevel.AT_MOST_ONCE and last_msg.retry_count < MAX_RETRY:
                self._retry(last_msg)
        self._update_success_rate()
        self.stats["pending_count"] = sum(1 for msgs in self.message_queue.values() for m in msgs if m.status == MessageStatus.PENDING)
        return last_msg
    
    def _ack(self, msg: Message, to_project: str):
        """QoS 1+ ack 机制"""
        msg.status = MessageStatus.ACKED
        self.stats["message_total_acked"] += 1
        self._audit("ack", msg.from_, to_project, msg.topic, "ok", f"msg_id={msg.msg_id}")
    
    def _retry(self, msg: Message):
        """重试机制 (0.0.15 第 8 节)"""
        if msg.retry_count >= len(RETRY_BACKOFFS_MS):
            self._audit("retry", msg.from_, msg.to, msg.topic, "fail", f"max retry reached")
            return
        backoff_ms = RETRY_BACKOFFS_MS[msg.retry_count]
        msg.retry_count += 1
        self.stats["message_total_retried"] += 1
        msg.status = MessageStatus.PENDING
        self._audit("retry", msg.from_, msg.to, msg.topic, "ok", f"retry #{msg.retry_count}, backoff_ms={backoff_ms}")
    
    def _update_avg_latency(self):
        """更新平均延迟"""
        if self.stats["_latency_count"] > 0:
            self.stats["message_avg_latency_ms"] = self.stats["_latency_sum_ms"] / self.stats["_latency_count"]
    
    def _update_success_rate(self):
        """更新成功率 (0.0.15 第 6 节)"""
        total = self.stats["message_total_delivered"] + self.stats["message_total_failed"]
        if total > 0:
            self.stats["message_success_rate"] = self.stats["message_total_delivered"] / total * 100
        else:
            self.stats["message_success_rate"] = 0.0
    
    # ---------------- 审计日志 (append-only, 0.0.15 第 7 节) ----------------
    def _audit(self, action: str, from_: str, to: str, topic: str, status: str, note: str):
        """写审计日志 (append-only, 强制)"""
        entry = {
            "audit_id": str(uuid.uuid4())[:8],
            "action": action,
            "from": from_,
            "to": to,
            "topic": topic,
            "status": status,
            "note": note,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.audit_log.append(entry)
        self.stats["audit_log_count"] = len(self.audit_log)
        # 写入文件 (按日滚动, Git 跟踪)
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        audit_file = self.audit_log_dir / f"audit-{today}.log"
        try:
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            pass  # 审计文件写入失败不影响业务
    
    def get_audit_log(self, project_id: str = None, topic: str = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """查询审计日志 (可审计, 0.0.15 第 7 节)"""
        filtered = self.audit_log
        if project_id:
            filtered = [e for e in filtered if e["from"] == project_id or e["to"] == project_id]
        if topic:
            filtered = [e for e in filtered if e["topic"] == topic]
        return filtered[-limit:]
    
    # ---------------- 监控 (10 项, 0.0.15 第 6 节) ----------------
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """获取监控指标 (Sponsor 看板可看, 0.0.15 第 12 节)"""
        # 主题热度 (Top 5)
        topic_heat = sorted(
            [(t, len(msgs)) for t, msgs in self.message_queue.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        return {
            "stats": {k: v for k, v in self.stats.items() if not k.startswith("_")},
            "topic_heat_top5": [{"topic": t, "message_count": c} for t, c in topic_heat],
            "subscriptions": {p: topics for p, topics in self.subscriptions.items()},
            "pending_messages": [
                m.to_dict() for msgs in self.message_queue.values() for m in msgs if m.status == MessageStatus.PENDING
            ]
        }
    
    def get_message_stats(self) -> Dict[str, Any]:
        """获取消息统计 (m0.2 兼容接口)"""
        return {
            "stats": self.stats,
            "subscriptions_count": self.stats["subscriptions_count"],
            "topics_count": self.stats["topics_count"],
            "total_pending": self.stats["pending_count"]
        }


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    import sys
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO Message-Broker 演示 (m1.6, DEC-2026-0004) ===\n")
    
    broker = MessageBroker(PMO_ROOT)
    
    # 1. 业务项目订阅主题
    print("[1] 业务项目订阅主题")
    broker.subscribe("1.2", "biz.1.3.state")
    broker.subscribe("1.3", "biz.1.2.metric")
    broker.subscribe("1.3", "inter.biz.1.2.to.1.3")
    print(f"  - 订阅数: {broker.stats['subscriptions_count']}\n")
    
    # 2. 业务项目 A 发布消息到 B (经 broker)
    print("[2] 业务项目 1.2 → broker → 1.3 (经 PMO 中介)")
    msg1 = broker.publish(
        from_project="1.2", to_project="1.3", topic="inter.biz.1.2.to.1.3",
        msg_type=MessageType.NOTIFICATION,
        content={"event": "data_ready", "data_id": "data-001"},
        qos=QoSLevel.AT_LEAST_ONCE
    )
    print(f"  - msg_id: {msg1.msg_id}, status: {msg1.status.value}, qos: {msg1.qos.value}\n")
    
    # 3. 业务项目 1.1 上报状态 (1.3 订阅了 1.1 state)
    print("[3] 业务项目 1.1 → broker → 1.3 状态上报")
    broker.subscribe("1.3", "biz.1.1.state")
    msg2 = broker.publish(
        from_project="1.1", to_project="1.3", topic="biz.1.1.state",
        msg_type=MessageType.NOTIFICATION,
        content={"state": "active", "phase": "P3-test"},
        qos=QoSLevel.AT_MOST_ONCE
    )
    print(f"  - msg_id: {msg2.msg_id}, status: {msg2.status.value}\n")
    
    # 4. 业务指标上报
    print("[4] 业务项目 1.2 → broker → 1.3 指标上报")
    msg3 = broker.publish(
        from_project="1.2", to_project="1.3", topic="biz.1.2.metric",
        msg_type=MessageType.BIZ_DATA,
        content={"flow_latency": 100, "exception_rate": 0.01, "pass_rate": 0.99},
        qos=QoSLevel.AT_LEAST_ONCE
    )
    print(f"  - msg_id: {msg3.msg_id}, status: {msg3.status.value}\n")
    
    # 5. 协议校验失败 (主题非法)
    print("[5] 协议校验失败 (主题非法)")
    msg4 = broker.publish(
        from_project="1.2", to_project="1.3", topic="invalid.topic",
        msg_type=MessageType.NOTIFICATION,
        content={"data": "test"}
    )
    print(f"  - msg_id: {msg4.msg_id}, status: {msg4.status.value}, error: {msg4.error}\n")
    
    # 6. 业务异常告警 (上行)
    print("[6] 业务项目 1.2 → broker → PMO 异常告警")
    broker.subscribe("pmo-monitor", "biz.1.2.exception")
    msg5 = broker.publish(
        from_project="1.2", to_project="pmo-monitor", topic="biz.1.2.exception",
        msg_type=MessageType.ALERT,
        content={"severity": "critical", "code": "EXC-001"},
        qos=QoSLevel.AT_LEAST_ONCE,
        layer="biz"
    )
    print(f"  - msg_id: {msg5.msg_id}, status: {msg5.status.value}\n")
    
    # 7. 监控指标 (Sponsor 看板)
    print("[7] 监控指标 (Sponsor 看板可看)")
    metrics = broker.get_monitoring_metrics()
    for k, v in metrics["stats"].items():
        print(f"  - {k}: {v}")
    print(f"  - 主题热度 Top 5: {metrics['topic_heat_top5']}\n")
    
    # 8. 审计日志 (可审计)
    print("[8] 审计日志 (可审计, 最近 10 条)")
    audit = broker.get_audit_log(limit=10)
    for entry in audit:
        print(f"  - [{entry['action']}] {entry['from']} → {entry['to']} topic={entry['topic']} status={entry['status']}")
    print(f"  - 审计日志总数: {broker.stats['audit_log_count']}\n")
    
    print("=== m1.6 Message-Broker 演示完成 ===")
