"""
PMO 反射 (reflect.py)
- agent 反射: 看自己状态/历史/反思
- 0.0.8 自进化: 反思 → 规则演进
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


class ReflectionType(str, Enum):
    OBSERVATION = "observation"      # 观察
    INSIGHT = "insight"              # 洞察
    IMPROVEMENT = "improvement"      # 改进
    LEARNING = "learning"            # 学习
    SELF_CRITICISM = "self-criticism"  # 自我批评


class Reflection:
    """反思"""
    
    def __init__(self, agent_name: str, reflection_type: ReflectionType, content: str, action_items: List[str] = None):
        self.reflection_id = f"REFL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self.agent_name = agent_name
        self.reflection_type = reflection_type
        self.content = content
        self.action_items = action_items or []
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.applied = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reflection_id": self.reflection_id,
            "agent_name": self.agent_name,
            "reflection_type": self.reflection_type.value,
            "content": self.content,
            "action_items": self.action_items,
            "timestamp": self.timestamp,
            "applied": self.applied
        }


class ReflectionManager:
    """反思管理器"""
    
    def __init__(self):
        self.reflections: List[Reflection] = []
        self.evolutions_triggered = 0
    
    def reflect(self, agent_name: str, reflection_type: ReflectionType, content: str, action_items: List[str] = None) -> Reflection:
        """记录反思"""
        r = Reflection(agent_name, reflection_type, content, action_items)
        self.reflections.append(r)
        return r
    
    def trigger_evolution(self, reflection_id: str) -> bool:
        """触发自进化 (0.0.8)"""
        for r in self.reflections:
            if r.reflection_id == reflection_id:
                r.applied = True
                self.evolutions_triggered += 1
                return True
        return False
    
    def get_reflections(self, agent_name: str = None, reflection_type: ReflectionType = None) -> List[Dict[str, Any]]:
        results = self.reflections
        if agent_name:
            results = [r for r in results if r.agent_name == agent_name]
        if reflection_type:
            results = [r for r in results if r.reflection_type == reflection_type]
        return [r.to_dict() for r in results]
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_reflections": len(self.reflections),
            "by_type": {
                rt.value: sum(1 for r in self.reflections if r.reflection_type == rt)
                for rt in ReflectionType
            },
            "evolutions_triggered": self.evolutions_triggered
        }


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    print("=== PMO 反思演示 (0.0.8 自进化) ===\n")
    
    rm = ReflectionManager()
    
    # 1. Plan-Agent 观察
    print("[1] Plan-Agent 观察")
    r1 = rm.reflect("Plan-Agent", ReflectionType.OBSERVATION, "L1 PMO-Main 状态: running, 管理 1 个业务项目 (1.1)")
    print(f"  - {r1.reflection_id}: {r1.reflection_type.value}\n")
    
    # 2. Engineer-Agent 洞察
    print("[2] Engineer-Agent 洞察")
    r2 = rm.reflect("Engineer-Agent", ReflectionType.INSIGHT, "0.0.7 解耦原则: 治理规则不绑工程, Python 实现不锁定具体框架 (M7 选型)")
    print(f"  - {r2.reflection_id}: {r2.reflection_type.value}\n")
    
    # 3. Reviewer-Agent 改进
    print("[3] Reviewer-Agent 改进")
    r3 = rm.reflect(
        "Reviewer-Agent", ReflectionType.IMPROVEMENT,
        "建议: 业务指标 5 项可加自定义指标, 但需符合 schema.json",
        action_items=["m1.3 业务指标支持业务项目自定义", "m1.2 指标审计验证自定义指标"]
    )
    print(f"  - {r3.reflection_id}: {r3.reflection_type.value}")
    print(f"  - 行动项: {r3.action_items}\n")
    
    # 4. PMO-Main 学习
    print("[4] PMO-Main 学习")
    r4 = rm.reflect("PMO-Main", ReflectionType.LEARNING, "1 套 PMO 规范 + 1 个 PMO 实例 + N 项目 (0.0.10), 比 1 总+项目 PMO 更简洁")
    print(f"  - {r4.reflection_id}: {r4.reflection_type.value}\n")
    
    # 5. Sponsor 自我批评
    print("[5] Sponsor 自我批评")
    r5 = rm.reflect(
        "Sponsor", ReflectionType.SELF_CRITICISM,
        "应该更早提出 1 套规范 N 项目复用的想法, 避免了我之前 5 层 + 多 PMO 的过度设计",
        action_items=["建立平等讨论机制", "0.0.10 已记录 Sponsor 平等讨论后修订"]
    )
    print(f"  - {r5.reflection_id}: {r5.reflection_type.value}\n")
    
    # 6. 触发自进化
    print("[6] 触发自进化 (0.0.8)")
    rm.trigger_evolution(r3.reflection_id)
    print(f"  - {r3.reflection_id} 触发自进化\n")
    
    # 7. 反思统计
    print("[7] 反思统计")
    stats = rm.get_statistics()
    print(f"  - 总反思: {stats['total_reflections']} 条")
    print(f"  - 按类型: {stats['by_type']}")
    print(f"  - 触发自进化: {stats['evolutions_triggered']} 次")
