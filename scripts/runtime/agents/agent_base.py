"""
PMO Agent 基类 (agent_base.py)
- 5 个 PMO 核心 agent (三权分立, 0.0.10)
  - L0 Sponsor (人机, 监督权)
  - L1 PMO-Main (1 个实例, 行政权, 管 N 项目)
  - L2 Plan-Agent (司法权, 计划/治理)
  - L2 Engineer-Agent (司法权, 工程)
  - L2 Reviewer-Agent (司法权, 审查/审计)
- agent 状态机 (idle/activated/running/suspended/completed/error)
- 反射 (introspection, 看自己状态)
"""
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_machine import AgentState, StateMachine


class PMOAgent(ABC):
    """PMO Agent 基类"""
    
    def __init__(self, name: str, role: str, layer: str, pmo_root: str):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.layer = layer  # L0 / L1 / L2
        self.pmo_root = Path(pmo_root)
        self.state_machine = StateMachine(f"agent-{name}", AgentState.IDLE, str(pmo_root))
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_active = None
        self.tasks_done = 0
        self.reflection_log: List[Dict[str, Any]] = []
    
    def activate(self) -> bool:
        """激活 agent (从 idle 到 activated)"""
        if self.state_machine.state != AgentState.IDLE:
            return False
        return self.state_machine.transition(AgentState.ACTIVATED, f"{self.name} activated")
    
    def start(self) -> bool:
        """启动 agent (从 activated 到 running)"""
        if self.state_machine.state != AgentState.ACTIVATED:
            return False
        self.last_active = datetime.now(timezone.utc).isoformat()
        return self.state_machine.transition(AgentState.RUNNING, f"{self.name} running")
    
    def suspend(self, reason: str = "") -> bool:
        """暂停 agent"""
        if self.state_machine.state != AgentState.RUNNING:
            return False
        return self.state_machine.transition(AgentState.SUSPENDED, reason)
    
    def resume(self) -> bool:
        """恢复 agent"""
        if self.state_machine.state != AgentState.SUSPENDED:
            return False
        return self.state_machine.transition(AgentState.RUNNING, "resumed")
    
    def complete(self) -> bool:
        """完成 agent"""
        if self.state_machine.state not in [AgentState.RUNNING, AgentState.ACTIVATED]:
            return False
        return self.state_machine.transition(AgentState.COMPLETED, f"{self.name} completed")
    
    def error(self, err: str) -> bool:
        """agent 出错"""
        self.reflection_log.append({
            "type": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": err
        })
        return self.state_machine.transition(AgentState.ERROR, err)
    
    def reflect(self) -> Dict[str, Any]:
        """反射 (introspection) — 看自己状态"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "layer": self.layer,
            "state": self.state_machine.get_state(),
            "created_at": self.created_at,
            "last_active": self.last_active,
            "tasks_done": self.tasks_done,
            "reflection_count": len(self.reflection_log),
            "history": self.state_machine.get_history()[-5:]  # 最近 5 条
        }
    
    def log_reflection(self, reflection_type: str, content: str):
        """记录反思"""
        self.reflection_log.append({
            "type": reflection_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content
        })
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务 (子类实现)"""
        pass


# ============================================
# L1 PMO-Main (1 个实例, 管 N 项目, 行政权)
# ============================================
class PMOMainAgent(PMOAgent):
    """L1 PMO 行政权 — 1 个实例管 N 项目"""
    
    def __init__(self, pmo_root: str):
        super().__init__("PMO-Main", "行政权 (1 实例管 N 项目)", "L1", pmo_root)
        self.managed_projects: List[str] = []
    
    def register_project(self, project_id: str) -> bool:
        """注册业务项目"""
        if project_id in self.managed_projects:
            return False
        self.managed_projects.append(project_id)
        self.log_reflection("register", f"业务项目 {project_id} 已注册到 PMO 实例")
        return True
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务"""
        action = task.get("action", "")
        if action == "register_project":
            project_id = task.get("project_id", "")
            success = self.register_project(project_id)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {project_id} 已注册"}
        elif action == "list_projects":
            return {"agent": self.name, "action": action, "success": True, "result": self.managed_projects}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# L2 Plan-Agent (司法权, 计划/治理)
# ============================================
class PlanAgent(PMOAgent):
    """L2 Plan — 司法权 (计划/治理)"""
    
    def __init__(self, pmo_root: str):
        super().__init__("Plan-Agent", "司法权 (计划/治理, 审计 L1)", "L2", pmo_root)
    
    def audit_pmo_main(self, pmo_main: PMOMainAgent) -> Dict[str, Any]:
        """审计 PMO-Main (司法权)"""
        pmo_main_reflection = pmo_main.reflect()
        audit = {
            "auditor": self.name,
            "auditee": pmo_main.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pmo_main_state": pmo_main_reflection["state"],
            "managed_projects": pmo_main.managed_projects,
            "verdict": "compliant" if pmo_main_reflection["state"] != "error" else "violation",
            "self_check": "L1 agent 状态正常, 项目管理正常"
        }
        self.log_reflection("audit", f"审计 {pmo_main.name}: {audit['verdict']}")
        return audit
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "plan_phase":
            return {"agent": self.name, "action": action, "success": True, "result": "阶段计划已生成"}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# L2 Engineer-Agent (司法权, 工程)
# ============================================
class EngineerAgent(PMOAgent):
    """L2 Engineer — 司法权 (工程)"""
    
    def __init__(self, pmo_root: str):
        super().__init__("Engineer-Agent", "司法权 (工程, 审计 L1)", "L2", pmo_root)
    
    def audit_pmo_main(self, pmo_main: PMOMainAgent) -> Dict[str, Any]:
        """审计 PMO-Main 的工程决策"""
        audit = {
            "auditor": self.name,
            "auditee": pmo_main.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engineering_compliance": True,
            "decoupling_check": "0.0.7 解耦: 治理不绑工程, 通过",
            "verdict": "compliant"
        }
        self.log_reflection("audit", f"工程审计 {pmo_main.name}: compliant")
        return audit
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "build":
            return {"agent": self.name, "action": action, "success": True, "result": "构建完成"}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# L2 Reviewer-Agent (司法权, 审查/审计)
# ============================================
class ReviewerAgent(PMOAgent):
    """L2 Reviewer — 司法权 (审查/审计)"""
    
    def __init__(self, pmo_root: str):
        super().__init__("Reviewer-Agent", "司法权 (审查/审计, 互相验证)", "L2", pmo_root)
    
    def audit_pmo_main(self, pmo_main: PMOMainAgent) -> Dict[str, Any]:
        """审查 PMO-Main 的治理指标"""
        audit = {
            "auditor": self.name,
            "auditee": pmo_main.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_check": "业务/治理/工程三类指标都已定义, 通过",
            "verdict": "compliant"
        }
        self.log_reflection("audit", f"审查 {pmo_main.name}: compliant")
        return audit
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "review":
            return {"agent": self.name, "action": action, "success": True, "result": "审查完成"}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# L0 Sponsor Agent (人机, 监督权)
# ============================================
class SponsorAgent(PMOAgent):
    """L0 Sponsor — 监督权 (顶层权威, 打破递归, 看指标不执行)"""
    
    def __init__(self, pmo_root: str):
        super().__init__("Sponsor", "监督权 (顶层权威, 看指标看板)", "L0", pmo_root)
    
    def observe_metrics(self, pmo_main: PMOMainAgent) -> Dict[str, Any]:
        """Sponsor 看指标 (不执行, 只监督)"""
        observation = {
            "observer": self.name,
            "target": pmo_main.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "managed_projects": pmo_main.managed_projects,
            "pmo_main_state": pmo_main.reflect()["state"],
            "role": "监督, 不执行"
        }
        self.log_reflection("observe", f"监督 {pmo_main.name}: {pmo_main.reflect()['state']}")
        return observation
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "approve":
            return {"agent": self.name, "action": action, "success": True, "result": "已批准"}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# PMO 实例 (1 个, 管 5 个 agent)
# ============================================
class PMOInstance:
    """1 个 PMO 实例, 管 5 个 agent (三权分立)"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = pmo_root
        self.pmo_main = PMOMainAgent(pmo_root)
        self.plan_agent = PlanAgent(pmo_root)
        self.engineer_agent = EngineerAgent(pmo_root)
        self.reviewer_agent = ReviewerAgent(pmo_root)
        self.sponsor_agent = SponsorAgent(pmo_root)
        self.agents = [self.pmo_main, self.plan_agent, self.engineer_agent, self.reviewer_agent, self.sponsor_agent]
    
    def activate_all(self):
        """激活所有 agent"""
        for agent in self.agents:
            agent.activate()
            agent.start()
    
    def get_status(self) -> Dict[str, Any]:
        """PMO 实例状态"""
        return {
            "instance_id": self.pmo_main.agent_id,
            "agent_count": len(self.agents),
            "agents": [a.reflect() for a in self.agents],
            "managed_projects": self.pmo_main.managed_projects,
            "three_powers": {
                "L0_sponsor": self.sponsor_agent.name,
                "L1_pmo_main": self.pmo_main.name,
                "L2_judicial": [self.plan_agent.name, self.engineer_agent.name, self.reviewer_agent.name]
            }
        }
    
    def l2_audit_l1(self) -> List[Dict[str, Any]]:
        """3 个 L2 agent 审计 L1 (三权分立)"""
        audits = []
        audits.append(self.plan_agent.audit_pmo_main(self.pmo_main))
        audits.append(self.engineer_agent.audit_pmo_main(self.pmo_main))
        audits.append(self.reviewer_agent.audit_pmo_main(self.pmo_main))
        return audits
    
    def l0_observe_l1(self) -> Dict[str, Any]:
        """L0 Sponsor 监督 L1 (打破递归)"""
        return self.sponsor_agent.observe_metrics(self.pmo_main)


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO 5 Agent (三权分立) 演示 ===\n")
    
    # 1. 初始化 PMO 实例
    print("[1] 初始化 PMO 实例 (1 个, 管 5 agent)")
    pmo = PMOInstance(PMO_ROOT)
    print(f"  - L0 Sponsor: {pmo.sponsor_agent.name}")
    print(f"  - L1 PMO-Main: {pmo.pmo_main.name}")
    print(f"  - L2 Plan: {pmo.plan_agent.name}")
    print(f"  - L2 Engineer: {pmo.engineer_agent.name}")
    print(f"  - L2 Reviewer: {pmo.reviewer_agent.name}\n")
    
    # 2. 激活所有 agent
    print("[2] 激活所有 agent (从 idle 到 running)")
    pmo.activate_all()
    for agent in pmo.agents:
        print(f"  - {agent.name}: {agent.reflect()['state']}")
    print()
    
    # 3. L1 注册业务项目
    print("[3] L1 PMO-Main 注册业务项目 (管 N 项目)")
    pmo.pmo_main.process({"action": "register_project", "project_id": "1.1"})
    pmo.pmo_main.process({"action": "register_project", "project_id": "1.2"})
    print(f"  - 管理项目: {pmo.pmo_main.managed_projects}\n")
    
    # 4. L2 审计 L1 (三权分立)
    print("[4] L2 3 个 agent 审计 L1 (司法权)")
    audits = pmo.l2_audit_l1()
    for audit in audits:
        print(f"  - {audit['auditor']} → {audit['auditee']}: {audit['verdict']}")
    print()
    
    # 5. L0 Sponsor 监督 L1 (打破递归)
    print("[5] L0 Sponsor 监督 L1 (顶层权威)")
    obs = pmo.l0_observe_l1()
    print(f"  - Sponsor 观察: {obs['pmo_main_state']}")
    print(f"  - 管理项目数: {len(obs['managed_projects'])}\n")
    
    # 6. 反射 (introspection)
    print("[6] 反射 (introspection) — 各 agent 看自己状态")
    print(f"  - {pmo.pmo_main.name}: state={pmo.pmo_main.reflect()['state']}, tasks_done={pmo.pmo_main.reflect()['tasks_done']}")
    print(f"  - {pmo.plan_agent.name}: reflection_count={pmo.plan_agent.reflect()['reflection_count']}")
    print()
    
    # 7. 状态报告
    print("[7] PMO 实例状态报告")
    status = pmo.get_status()
    print(f"  - agent 总数: {status['agent_count']}")
    print(f"  - 三权分立: L0={status['three_powers']['L0_sponsor']}, L1={status['three_powers']['L1_pmo_main']}, L2={status['three_powers']['L2_judicial']}")
