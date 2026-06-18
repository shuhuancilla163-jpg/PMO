"""
PMO 触发器 (triggers.py)
- 4 类触发: 时间触发 / 事件触发 / 状态触发 / 手动触发
- 触发后激活 agent
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
from threading import Timer

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TriggerType(str, Enum):
    TIME = "time"            # 时间触发 (定时)
    EVENT = "event"          # 事件触发 (状态变化/外部事件)
    STATE = "state"          # 状态触发 (状态机达到某状态)
    MANUAL = "manual"        # 手动触发 (Sponsor / agent 触发)


class Trigger:
    """触发器"""
    
    def __init__(self, trigger_id: str, trigger_type: TriggerType, condition: str, action: str, description: str = ""):
        self.trigger_id = trigger_id
        self.trigger_type = trigger_type
        self.condition = condition
        self.action = action
        self.description = description
        self.enabled = True
        self.last_fired = None
        self.fire_count = 0
        self.created_at = datetime.now(timezone.utc).isoformat()
    
    def fire(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """触发"""
        self.last_fired = datetime.now(timezone.utc).isoformat()
        self.fire_count += 1
        return {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "action": self.action,
            "context": context or {},
            "fired_at": self.last_fired
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "condition": self.condition,
            "action": self.action,
            "description": self.description,
            "enabled": self.enabled,
            "last_fired": self.last_fired,
            "fire_count": self.fire_count,
            "created_at": self.created_at
        }


class TriggerManager:
    """触发器管理器"""
    
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}
        self.event_log: List[Dict[str, Any]] = []
    
    def register(self, trigger: Trigger):
        """注册触发器"""
        self.triggers[trigger.trigger_id] = trigger
    
    def fire(self, trigger_id: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """触发"""
        trigger = self.triggers.get(trigger_id)
        if not trigger or not trigger.enabled:
            return None
        result = trigger.fire(context)
        self.event_log.append(result)
        return result
    
    def list_triggers(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.triggers.values()]
    
    def get_event_log(self) -> List[Dict[str, Any]]:
        return self.event_log


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    print("=== PMO 触发器演示 ===\n")
    
    tm = TriggerManager()
    
    # 1. 时间触发器
    print("[1] 时间触发器 (每天早上 9 点跑指标)")
    t1 = Trigger(
        trigger_id="T-001",
        trigger_type=TriggerType.TIME,
        condition="cron: 0 9 * * *",
        action="run_daily_metrics",
        description="每天早上 9 点跑业务指标"
    )
    tm.register(t1)
    print(f"  - 已注册: {t1.trigger_id} ({t1.trigger_type.value})\n")
    
    # 2. 事件触发器
    print("[2] 事件触发器 (业务异常时通知 PMO 实例)")
    t2 = Trigger(
        trigger_id="T-002",
        trigger_type=TriggerType.EVENT,
        condition="biz_exception_rate > 0.2",
        action="notify_pmo_instance",
        description="业务异常率超 20%, 通知 PMO 实例"
    )
    tm.register(t2)
    print(f"  - 已注册: {t2.trigger_id} ({t2.trigger_type.value})\n")
    
    # 3. 状态触发器
    print("[3] 状态触发器 (业务项目状态=active 时启动监控)")
    t3 = Trigger(
        trigger_id="T-003",
        trigger_type=TriggerType.STATE,
        condition="biz_project_state == 'active'",
        action="start_monitoring",
        description="业务项目激活时启动监控"
    )
    tm.register(t3)
    print(f"  - 已注册: {t3.trigger_id} ({t3.trigger_type.value})\n")
    
    # 4. 手动触发器
    print("[4] 手动触发器 (Sponsor 介入节点)")
    t4 = Trigger(
        trigger_id="T-004",
        trigger_type=TriggerType.MANUAL,
        condition="sponsor_intervention",
        action="sponsor_review",
        description="Sponsor 介入: 启动/重大决策/验收"
    )
    tm.register(t4)
    print(f"  - 已注册: {t4.trigger_id} ({t4.trigger_type.value})\n")
    
    # 5. 触发演示
    print("[5] 触发演示")
    result = tm.fire("T-001", {"time": "2026-06-18T09:00:00Z"})
    print(f"  - T-001 触发: {result['action']}")
    result = tm.fire("T-002", {"exception_rate": 0.25})
    print(f"  - T-002 触发: {result['action']}")
    result = tm.fire("T-003", {"biz_project": "1.1"})
    print(f"  - T-003 触发: {result['action']}")
    result = tm.fire("T-004", {"sponsor": "Sponsor"})
    print(f"  - T-004 触发: {result['action']}\n")
    
    # 6. 事件日志
    print(f"[6] 事件日志 (共 {len(tm.get_event_log())} 条)")
    print(f"  - 已注册触发器: {len(tm.list_triggers())} 个")
