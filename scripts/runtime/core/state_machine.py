"""
PMO 状态机 (state_machine.py)
- 业务项目状态机 (m2.6)
- 任务状态机 (P0-init / P1-spec / P2-impl / P3-test / P4-deploy / P5-archive)
- agent 状态机 (idle / activated / running / suspended / completed)
- 3 层异常拦截 (PMO 规范不参与业务, PMO 实例拦截项目级, 业务项目拦截自身)
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any

# ============================================
# 阶段门控 (PMO 治理层, 不参与业务)
# ============================================
class PhaseGate(str, Enum):
    P0_INIT = "P0-init"            # 初始化
    P1_SPEC = "P1-spec"            # 规范
    P2_IMPL = "P2-impl"            # 实施
    P3_TEST = "P3-test"            # 测试
    P4_DEPLOY = "P4-deploy"        # 部署
    P5_ARCHIVE = "P5-archive"      # 归档


# ============================================
# 业务项目状态 (PMO 实例管, 项目级)
# ============================================
class BizProjectState(str, Enum):
    REGISTERED = "registered"      # 已注册
    ACTIVE = "active"              # 活跃
    PAUSED = "paused"              # 暂停
    BLOCKED = "blocked"            # 阻塞
    COMPLETED = "completed"        # 已完成
    ARCHIVED = "archived"          # 已归档
    CANCELED = "canceled"          # 已取消 (美式拼写, 避免 enum 重名)


# ============================================
# 任务状态
# ============================================
class TaskState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============================================
# Agent 状态
# ============================================
class AgentState(str, Enum):
    IDLE = "idle"
    ACTIVATED = "activated"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ERROR = "error"


# ============================================
# 异常级别 (3 层, 0.0.10)
# ============================================
class ExceptionLayer(str, Enum):
    PMO_SPEC = "L0-pmo-spec"           # PMO 规范 (不参与业务, 标准+监督)
    PMO_INSTANCE = "L1-pmo-instance"   # PMO 实例 (拦截项目级, 含自身)
    BIZ_PROJECT = "L2-biz-project"     # 业务项目 (拦截自身)


# ============================================
# 异常严重性
# ============================================
class ExceptionSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================
# 状态机实现
# ============================================
class StateMachine:
    """通用状态机"""
    
    def __init__(self, name: str, initial_state: Enum, pmo_root: str):
        self.name = name
        self.state = initial_state
        self.pmo_root = Path(pmo_root)
        self.history = [(initial_state, datetime.now(timezone.utc).isoformat())]
    
    def transition(self, new_state: Enum, reason: str = "") -> bool:
        """状态转换"""
        old_state = self.state
        self.state = new_state
        timestamp = datetime.now(timezone.utc).isoformat()
        self.history.append((new_state, timestamp, reason))
        print(f"[{self.name}] {old_state.value} → {new_state.value} ({reason})")
        return True
    
    def get_state(self) -> str:
        return self.state.value
    
    def get_history(self) -> list:
        return self.history
    
    def save(self, path: Path):
        """保存状态机历史"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "name": self.name,
                "current_state": self.state.value,
                "history": [(s.value if hasattr(s, 'value') else s, t, r) for s, t, *r in self.history]
            }, f, indent=2, ensure_ascii=False)
    
    def load(self, path: Path) -> bool:
        """加载状态机"""
        if not path.exists():
            return False
        with open(path) as f:
            data = json.load(f)
        self.state = type(self.state)(data["current_state"])
        self.history = data["history"]
        return True


# ============================================
# 业务项目状态机 (PMO 实例用)
# ============================================
class BizProjectStateMachine(StateMachine):
    """业务项目状态机 (PMO 实例管, 项目级)"""
    
    VALID_TRANSITIONS = {
        BizProjectState.REGISTERED: [BizProjectState.ACTIVE, BizProjectState.CANCELED],
        BizProjectState.ACTIVE: [BizProjectState.PAUSED, BizProjectState.BLOCKED, BizProjectState.COMPLETED, BizProjectState.ARCHIVED],
        BizProjectState.PAUSED: [BizProjectState.ACTIVE, BizProjectState.ARCHIVED, BizProjectState.CANCELED],
        BizProjectState.BLOCKED: [BizProjectState.ACTIVE, BizProjectState.ARCHIVED, BizProjectState.CANCELED],
        BizProjectState.COMPLETED: [BizProjectState.ARCHIVED],
        BizProjectState.ARCHIVED: [],
        BizProjectState.CANCELED: [],
    }
    
    def __init__(self, project_id: str, pmo_root: str):
        super().__init__(f"biz-project-{project_id}", BizProjectState.REGISTERED, pmo_root)
        self.project_id = project_id
    
    def transition(self, new_state: BizProjectState, reason: str = "") -> bool:
        valid = self.VALID_TRANSITIONS.get(self.state, [])
        if new_state not in valid:
            print(f"[biz-project-{self.project_id}] ❌ INVALID transition: {self.state.value} → {new_state.value}")
            return False
        return super().transition(new_state, reason)


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO 状态机演示 ===\n")
    
    # 1. 业务项目状态机
    print("[1] 业务项目状态机")
    bpsm = BizProjectStateMachine("1.1", PMO_ROOT)
    bpsm.transition(BizProjectState.ACTIVE, "1.1 已注册, 启动")
    bpsm.transition(BizProjectState.COMPLETED, "M0-M7 全部完成")
    bpsm.transition(BizProjectState.ARCHIVED, "项目归档")
    print(f"当前状态: {bpsm.get_state()}\n")
    
    # 2. 异常转换 (无效)
    print("[2] 异常转换 (验证状态机合法性)")
    bpsm2 = BizProjectStateMachine("test", PMO_ROOT)
    bpsm2.transition(BizProjectState.ARCHIVED, "尝试从 registered 直接到 archived")
    print()
    
    # 3. 保存状态
    print("[3] 状态保存")
    bpsm.save(Path(PMO_ROOT) / "tasks" / "state" / "1.1-pmo-self.json")
    print(f"已保存到 tasks/state/1.1-pmo-self.json")
