"""
PMO 通信协议 (protocol.py)
- agent ↔ agent 通信 (L1↔L2, L0↔L1, L2↔L2)
- agent ↔ 业务项目通信 (PMO↔业务)
- 消息类型: request/response/notification/alert/escalation
- JSON 协议, 异步, 可审计
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ALERT = "alert"
    ESCALATION = "escalation"


class Message:
    """PMO 消息"""
    
    def __init__(self, msg_type: MessageType, from_: str, to: str, content: Dict[str, Any], layer: str = ""):
        self.msg_id = str(uuid.uuid4())[:8]
        self.msg_type = msg_type
        self.from_ = from_
        self.to = to
        self.content = content
        self.layer = layer  # L0/L1/L2
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.read = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "from": self.from_,
            "to": self.to,
            "content": self.content,
            "layer": self.layer,
            "timestamp": self.timestamp,
            "read": self.read
        }


class Protocol:
    """PMO 通信协议"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List] = {}
    
    def send(self, msg: Message) -> Message:
        """发送消息"""
        self.messages.append(msg)
        # 通知订阅者
        if msg.to in self.subscribers:
            for sub in self.subscribers[msg.to]:
                sub(msg)
        return msg
    
    def request(self, from_: str, to: str, content: Dict[str, Any], layer: str = "") -> Message:
        """请求"""
        return self.send(Message(MessageType.REQUEST, from_, to, content, layer))
    
    def response(self, from_: str, to: str, content: Dict[str, Any], layer: str = "") -> Message:
        """响应"""
        return self.send(Message(MessageType.RESPONSE, from_, to, content, layer))
    
    def notification(self, from_: str, to: str, content: Dict[str, Any], layer: str = "") -> Message:
        """通知"""
        return self.send(Message(MessageType.NOTIFICATION, from_, to, content, layer))
    
    def alert(self, from_: str, to: str, content: Dict[str, Any], layer: str = "") -> Message:
        """告警"""
        return self.send(Message(MessageType.ALERT, from_, to, content, layer))
    
    def escalation(self, from_: str, to: str, content: Dict[str, Any], layer: str = "") -> Message:
        """升级"""
        return self.send(Message(MessageType.ESCALATION, from_, to, content, layer))
    
    def subscribe(self, agent_name: str, callback):
        """订阅"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
    
    def get_messages(self, agent_name: str = None) -> List[Dict[str, Any]]:
        """获取消息"""
        if agent_name:
            return [m.to_dict() for m in self.messages if m.to == agent_name or m.from_ == agent_name]
        return [m.to_dict() for m in self.messages]


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    print("=== PMO 通信协议演示 ===\n")
    
    proto = Protocol()
    
    # 1. L1 PMO-Main 通知 L2 Plan-Agent
    print("[1] L1 → L2 通知 (PMO-Main → Plan-Agent)")
    msg1 = proto.notification("PMO-Main", "Plan-Agent", {"action": "audit", "biz_project": "1.1"}, "L1→L2")
    print(f"  - {msg1.msg_id}: {msg1.msg_type.value} ({msg1.from_} → {msg1.to})\n")
    
    # 2. L2 Plan-Agent 响应 L1
    print("[2] L2 → L1 响应 (Plan-Agent → PMO-Main)")
    msg2 = proto.response("Plan-Agent", "PMO-Main", {"verdict": "compliant"}, "L2→L1")
    print(f"  - {msg2.msg_id}: {msg2.msg_type.value} ({msg2.from_} → {msg2.to})\n")
    
    # 3. L0 Sponsor 监督 L1
    print("[3] L0 → L1 监督 (Sponsor → PMO-Main)")
    msg3 = proto.request("Sponsor", "PMO-Main", {"action": "observe_metrics"}, "L0→L1")
    print(f"  - {msg3.msg_id}: {msg3.msg_type.value} ({msg3.from_} → {msg3.to})\n")
    
    # 4. L1 → L0 升级
    print("[4] L1 → L0 升级 (PMO-Main → Sponsor, 重大异常)")
    msg4 = proto.escalation("PMO-Main", "Sponsor", {"severity": "critical", "code": "P002"}, "L1→L0")
    print(f"  - {msg4.msg_id}: {msg4.msg_type.value} ({msg4.from_} → {msg4.to})\n")
    
    # 5. L1 → 业务项目 通知
    print("[5] L1 → 业务项目 通知 (PMO-Main → 1.1-pmo-self)")
    msg5 = proto.notification("PMO-Main", "1.1-pmo-self", {"action": "register_success"}, "L1→biz")
    print(f"  - {msg5.msg_id}: {msg5.msg_type.value} ({msg5.from_} → {msg5.to})\n")
    
    # 6. 业务项目 → L1 告警
    print("[6] 业务项目 → L1 告警 (1.1-pmo-self → PMO-Main, 严重异常)")
    msg6 = proto.alert("1.1-pmo-self", "PMO-Main", {"severity": "critical", "exception_id": "EXC-..."}, "biz→L1")
    print(f"  - {msg6.msg_id}: {msg6.msg_type.value} ({msg6.from_} → {msg6.to})\n")
    
    # 7. 消息历史
    print(f"[7] 消息历史: {len(proto.get_messages())} 条")
