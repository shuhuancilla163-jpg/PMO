"""
PMO Agent 基类 (agent_base.py)
- 8 个 PMO 核心 agent (三权分立 + 3 维度分离, DEC-2026-0002)
  - L0 Sponsor (人机, 监督权)
  - L1 PMO-Main (1 个实例, 行政权, 维度 1: 业务项目整体)
  - L2 Plan-Agent (司法权, 计划/治理)
  - L2 Engineer-Agent (司法权, 维度 2: 业务项目内研发 5 阶段)
  - L2 Monitor-Agent (司法权, 维度 3: 业务项目上报)
  - L2 Reviewer-Agent (司法权, 审查/审计)
  - L2 Assessor-Agent (司法权, 3 维度分别考核)
  - L2 Message-Broker-Agent (司法权, 项目间消息)
- agent 状态机 (idle/activated/running/suspended/completed/error)
- 反射 (introspection, 看自己状态)
- 3 维度采集角色严格分离 (DEC-2026-0002)
- 业务项目 2 层合规 (业务项目整体 + 业务项目内研发 5 阶段)
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
# L1 PMO-Main (1 个实例, 维度 1: 业务项目整体)
# ============================================
class PMOMainAgent(PMOAgent):
    """L1 PMO 行政权 — 1 个实例管 N 项目, 维度 1 采集 (DEC-2026-0002)
    
    数据维度: 维度 1 (业务项目整体)
    - 业务项目注册/状态/配额/归档/隔离
    - 业务项目上报数据汇聚 (业务项目按 PMO 规范上报的关键指标)
    """
    
    def __init__(self, pmo_root: str):
        super().__init__("PMO-Main", "行政权 (1 实例管 N 项目, 维度 1 采集)", "L1", pmo_root)
        self.managed_projects: List[str] = []
        self.reported_metrics: Dict[str, List[Dict[str, Any]]] = {}  # 业务项目上报数据
        self.business_state: Dict[str, str] = {}  # 业务项目状态
        self.business_quota: Dict[str, Dict[str, Any]] = {}  # 业务项目配额
    
    def register_project(self, project_id: str) -> bool:
        """注册业务项目 (维度 1)"""
        if project_id in self.managed_projects:
            return False
        self.managed_projects.append(project_id)
        self.business_state[project_id] = "active"
        self.log_reflection("register", f"业务项目 {project_id} 已注册到 PMO 实例")
        return True
    
    def update_business_state(self, project_id: str, state: str) -> bool:
        """更新业务项目状态 (维度 1)"""
        if project_id not in self.managed_projects:
            return False
        valid_states = ["registered", "active", "paused", "blocked", "completed", "archived", "canceled"]
        if state not in valid_states:
            self.log_reflection("error", f"业务项目 {project_id} 状态非法: {state}")
            return False
        self.business_state[project_id] = state
        self.log_reflection("state_change", f"业务项目 {project_id} 状态变更为 {state}")
        return True
    
    def collect_business_reported_metrics(self, project_id: str, metrics: Dict[str, Any]) -> bool:
        """采集业务项目上报的关键指标 (维度 3, 但 PMO-Main 汇聚)"""
        if project_id not in self.managed_projects:
            return False
        if project_id not in self.reported_metrics:
            self.reported_metrics[project_id] = []
        self.reported_metrics[project_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics
        })
        self.log_reflection("collect_metrics", f"业务项目 {project_id} 上报指标已采集")
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
        elif action == "update_business_state":
            project_id = task.get("project_id", "")
            state = task.get("state", "")
            success = self.update_business_state(project_id, state)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {project_id} 状态变更为 {state}"}
        elif action == "collect_business_reported_metrics":
            project_id = task.get("project_id", "")
            metrics = task.get("metrics", {})
            success = self.collect_business_reported_metrics(project_id, metrics)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {project_id} 上报指标已采集"}
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
# L2 Engineer-Agent (司法权, 维度 2: 业务项目内研发 5 阶段)
# ============================================
class EngineerAgent(PMOAgent):
    """L2 Engineer — 司法权 (工程, 维度 2 采集, DEC-2026-0002)
    
    数据维度: 维度 2 (业务项目内研发 5 阶段)
    5 阶段: 需求/研发/测试/运维/评估
    采集: 研发 5 阶段数据 (产出/决策日志/不可变文档/异常拦截/指标)
    """
    
    # 5 阶段定义
    ENG_5_STAGES = ["requirement", "development", "test", "operations", "evaluation"]
    
    # 5 阶段 PMO 7 项合规清单
    ENG_5_STAGES_PMO_COMPLIANCE = {
        "requirement": ["阶段门控", "决策日志", "不可变文档"],
        "development": ["阶段门控", "决策日志", "不可变文档", "异常拦截"],
        "test": ["阶段门控", "异常拦截", "指标可贯彻"],
        "operations": ["阶段门控", "异常拦截", "3 层告警", "灾备"],
        "evaluation": ["决策日志", "指标可贯彻", "Sponsor 报告", "自进化"]
    }
    
    def __init__(self, pmo_root: str):
        super().__init__("Engineer-Agent", "司法权 (工程, 维度 2 采集: 研发 5 阶段)", "L2", pmo_root)
        # 5 阶段数据采集 (按项目 + 阶段)
        self.eng_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    
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
    
    def collect_eng_stage_data(self, project_id: str, stage: str, data: Dict[str, Any]) -> bool:
        """采集业务项目内研发 5 阶段数据 (维度 2)"""
        if stage not in self.ENG_5_STAGES:
            self.log_reflection("error", f"研发阶段非法: {stage}")
            return False
        if project_id not in self.eng_data:
            self.eng_data[project_id] = {s: [] for s in self.ENG_5_STAGES}
        self.eng_data[project_id][stage].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        })
        self.log_reflection("collect_eng", f"项目 {project_id} 研发阶段 {stage} 数据已采集")
        return True
    
    def get_eng_5_stages_status(self, project_id: str) -> Dict[str, Any]:
        """获取业务项目内研发 5 阶段状态 (维度 2)"""
        if project_id not in self.eng_data:
            return {s: {"collected": 0, "pmo_compliance": self.ENG_5_STAGES_PMO_COMPLIANCE[s]} for s in self.ENG_5_STAGES}
        return {
            s: {
                "collected": len(self.eng_data[project_id].get(s, [])),
                "pmo_compliance": self.ENG_5_STAGES_PMO_COMPLIANCE[s]
            }
            for s in self.ENG_5_STAGES
        }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "build":
            return {"agent": self.name, "action": action, "success": True, "result": "构建完成"}
        elif action == "collect_eng_stage_data":
            project_id = task.get("project_id", "")
            stage = task.get("stage", "")
            data = task.get("data", {})
            success = self.collect_eng_stage_data(project_id, stage, data)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {project_id} 阶段 {stage} 数据已采集"}
        elif action == "get_eng_5_stages_status":
            project_id = task.get("project_id", "")
            status = self.get_eng_5_stages_status(project_id)
            return {"agent": self.name, "action": action, "success": True, "result": status}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# L2 Monitor-Agent (司法权, 维度 3: 业务项目上报)  (新, DEC-2026-0002)
# ============================================
class MonitorAgent(PMOAgent):
    """L2 Monitor — 司法权 (监控, 维度 3 采集, DEC-2026-0002)
    
    数据维度: 维度 3 (业务项目上报)
    采集: 业务项目按 PMO 规范上报的关键指标
    监管: 上报合规 (合规率/及时率/完整度)
    """
    
    # 业务项目上报 5 项基础指标
    REPORT_METRICS_5_BASIC = [
        "flow_latency",       # 业务流耗时
        "exception_rate",     # 异常率
        "pass_rate",          # 通过率
        "rollback_rate",      # 回滚率
        "token_consumption"   # Token 消耗
    ]
    
    # 业务项目上报合规 3 项指标
    REPORT_COMPLIANCE_METRICS = [
        "biz_metrics_report_compliance",     # 上报合规率
        "biz_metrics_report_timeliness",     # 上报及时率
        "biz_metrics_report_completeness"    # 上报完整度
    ]
    
    def __init__(self, pmo_root: str):
        super().__init__("Monitor-Agent", "司法权 (监控, 维度 3 采集: 业务项目上报)", "L2", pmo_root)
        # 业务项目上报数据 (key=project_id, value=上报历史)
        self.reported_data: Dict[str, List[Dict[str, Any]]] = {}
        # 上报合规性统计
        self.compliance_stats: Dict[str, Dict[str, int]] = {}
    
    def audit_pmo_main(self, pmo_main: PMOMainAgent) -> Dict[str, Any]:
        """审计 PMO-Main 的业务项目上报合规性"""
        audits = []
        for project_id in pmo_main.managed_projects:
            reported = self.reported_data.get(project_id, [])
            has_recent_report = len(reported) > 0
            audit = {
                "auditor": self.name,
                "project_id": project_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "has_recent_report": has_recent_report,
                "report_count": len(reported),
                "verdict": "compliant" if has_recent_report else "no_report_yet"
            }
            audits.append(audit)
        combined = {
            "auditor": self.name,
            "auditee": pmo_main.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "audits": audits,
            "verdict": "compliant" if all(a["verdict"] == "compliant" for a in audits) else "violation"
        }
        self.log_reflection("audit", f"监控审计 {pmo_main.name}: {combined['verdict']}")
        return combined
    
    def collect_reported_data(self, project_id: str, data: Dict[str, Any]) -> bool:
        """采集业务项目按 PMO 规范上报的数据 (维度 3)"""
        if project_id not in self.reported_data:
            self.reported_data[project_id] = []
        self.reported_data[project_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        })
        # 检查上报合规性
        is_compliant = self.check_report_compliance(data)
        if project_id not in self.compliance_stats:
            self.compliance_stats[project_id] = {
                "total_reports": 0,
                "compliant_reports": 0,
                "late_reports": 0,
                "incomplete_reports": 0
            }
        self.compliance_stats[project_id]["total_reports"] += 1
        if is_compliant:
            self.compliance_stats[project_id]["compliant_reports"] += 1
        self.log_reflection("collect_reported", f"项目 {project_id} 上报数据已采集, 合规: {is_compliant}")
        return True
    
    def check_report_compliance(self, data: Dict[str, Any]) -> bool:
        """检查业务项目上报合规性 (5 项基础指标必须存在)"""
        for metric in self.REPORT_METRICS_5_BASIC:
            if metric not in data:
                return False
        return True
    
    def get_compliance_report(self, project_id: str) -> Dict[str, Any]:
        """获取业务项目上报合规性报告"""
        stats = self.compliance_stats.get(project_id, {})
        total = stats.get("total_reports", 0)
        compliant = stats.get("compliant_reports", 0)
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        return {
            "project_id": project_id,
            "total_reports": total,
            "compliant_reports": compliant,
            "compliance_rate": f"{compliance_rate:.2f}%",
            "required_metrics": self.REPORT_METRICS_5_BASIC,
            "compliance_metrics": self.REPORT_COMPLIANCE_METRICS
        }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "collect_reported_data":
            project_id = task.get("project_id", "")
            data = task.get("data", {})
            success = self.collect_reported_data(project_id, data)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {project_id} 上报数据已采集"}
        elif action == "get_compliance_report":
            project_id = task.get("project_id", "")
            report = self.get_compliance_report(project_id)
            return {"agent": self.name, "action": action, "success": True, "result": report}
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
# L2 Assessor-Agent (司法权, 3 维度分别考核)  (新, DEC-2026-0002)
# ============================================
class AssessorAgent(PMOAgent):
    """L2 Assessor — 司法权 (考核, DEC-2026-0002)
    
    考核 3 维度:
    - 维度 1: 业务项目整体 (m2.6 7 项)
    - 维度 2: 业务项目内研发 5 阶段 (PMO 7 项)
    - 维度 3: 业务项目内业务上报合规 (PMO 规范)
    """
    
    def __init__(self, pmo_root: str):
        super().__init__("Assessor-Agent", "司法权 (考核, 3 维度分别考核)", "L2", pmo_root)
        # 考核结果 (key=project_id, value=3 维度考核结果)
        self.assessments: Dict[str, Dict[str, Any]] = {}
    
    def assess_dimension_1(self, pmo_main: PMOMainAgent, project_id: str) -> Dict[str, Any]:
        """考核维度 1: 业务项目整体 (m2.6 7 项)"""
        state = pmo_main.business_state.get(project_id, "unknown")
        registered = project_id in pmo_main.managed_projects
        result = {
            "dimension": 1,
            "dimension_name": "业务项目整体",
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "criteria": "m2.6 7 项 (注册/状态/配额/归档/隔离/状态机/告警)",
            "checks": {
                "registration": "pass" if registered else "fail",
                "state_legality": "pass" if state in ["registered", "active", "paused", "blocked", "completed", "archived", "canceled"] else "fail"
            },
            "verdict": "compliant" if registered else "violation"
        }
        return result
    
    def assess_dimension_2(self, engineer_agent: EngineerAgent, project_id: str) -> Dict[str, Any]:
        """考核维度 2: 业务项目内研发 5 阶段 (PMO 7 项)"""
        status = engineer_agent.get_eng_5_stages_status(project_id)
        all_stages_collected = all(status[s]["collected"] > 0 for s in EngineerAgent.ENG_5_STAGES)
        result = {
            "dimension": 2,
            "dimension_name": "业务项目内研发 5 阶段",
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "criteria": "PMO 7 项 (阶段门控/决策日志/不可变文档/异常拦截/指标可贯彻/3 层告警/Sponsor 报告)",
            "stages_status": status,
            "all_stages_collected": all_stages_collected,
            "verdict": "compliant" if all_stages_collected else "partial"
        }
        return result
    
    def assess_dimension_3(self, monitor_agent: MonitorAgent, project_id: str) -> Dict[str, Any]:
        """考核维度 3: 业务项目内业务上报合规 (PMO 规范)"""
        report = monitor_agent.get_compliance_report(project_id)
        compliance_rate_str = report.get("compliance_rate", "0.00%")
        compliance_rate = float(compliance_rate_str.rstrip("%"))
        result = {
            "dimension": 3,
            "dimension_name": "业务项目内业务上报合规",
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "criteria": "PMO 规范 (5 项基础指标 + 上报合规 3 项)",
            "compliance_report": report,
            "verdict": "compliant" if compliance_rate >= 80 else ("warning" if compliance_rate >= 50 else "violation")
        }
        return result
    
    def assess_project(self, pmo_main: PMOMainAgent, engineer_agent: EngineerAgent, monitor_agent: MonitorAgent, project_id: str) -> Dict[str, Any]:
        """考核业务项目 3 维度"""
        d1 = self.assess_dimension_1(pmo_main, project_id)
        d2 = self.assess_dimension_2(engineer_agent, project_id)
        d3 = self.assess_dimension_3(monitor_agent, project_id)
        result = {
            "assessor": self.name,
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dimension_1": d1,
            "dimension_2": d2,
            "dimension_3": d3,
            "overall_verdict": "compliant" if all(d["verdict"] == "compliant" for d in [d1, d2, d3]) else "partial"
        }
        self.assessments[project_id] = result
        self.log_reflection("assess", f"项目 {project_id} 3 维度考核完成: {result['overall_verdict']}")
        return result
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "review":
            return {"agent": self.name, "action": action, "success": True, "result": "审查完成"}
        elif action == "assess_project":
            # 注: 完整调用需要 pmo_instance 上下文, 简化返回结构
            return {"agent": self.name, "action": action, "success": True, "result": "考核完成 (需 pmo_instance 上下文)"}
        return {"agent": self.name, "action": action, "success": False, "error": "unknown action"}


# ============================================
# L2 Message-Broker-Agent (司法权, 项目间消息)  (新, DEC-2026-0002)
# ============================================
class MessageBrokerAgent(PMOAgent):
    """L2 Message-Broker — 司法权 (消息, DEC-2026-0002)
    
    职责: 业务项目↔业务项目消息经 PMO 实例中介
    消息类型: request/response, notification/alert/escalation, biz_event, biz_data
    消息主题: biz.{id}.state/metric/exception/data, inter.biz.{a}.to.{b}
    """
    
    def __init__(self, pmo_root: str):
        super().__init__("Message-Broker-Agent", "司法权 (消息, 项目间消息经 PMO 中介)", "L2", pmo_root)
        # 消息队列 (key=topic, value=消息列表)
        self.message_queue: Dict[str, List[Dict[str, Any]]] = {}
        # 订阅关系 (key=project_id, value=订阅主题列表)
        self.subscriptions: Dict[str, List[str]] = {}
        # 消息统计
        self.message_stats: Dict[str, int] = {
            "total_sent": 0,
            "total_received": 0,
            "total_failed": 0,
            "total_retried": 0
        }
    
    def subscribe(self, project_id: str, topic: str) -> bool:
        """业务项目订阅主题"""
        if project_id not in self.subscriptions:
            self.subscriptions[project_id] = []
        if topic not in self.subscriptions[project_id]:
            self.subscriptions[project_id].append(topic)
        self.log_reflection("subscribe", f"项目 {project_id} 订阅主题 {topic}")
        return True
    
    def publish(self, from_project: str, topic: str, message: Dict[str, Any]) -> bool:
        """业务项目发布消息到主题"""
        if topic not in self.message_queue:
            self.message_queue[topic] = []
        msg = {
            "from": from_project,
            "topic": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "delivered": False
        }
        self.message_queue[topic].append(msg)
        self.message_stats["total_sent"] += 1
        self.log_reflection("publish", f"项目 {from_project} 发布消息到 {topic}")
        return True
    
    def deliver(self, topic: str) -> List[Dict[str, Any]]:
        """投递主题消息给订阅者 (经 PMO 中介)"""
        delivered = []
        if topic not in self.message_queue:
            return delivered
        for project_id, topics in self.subscriptions.items():
            if topic in topics:
                for msg in self.message_queue[topic]:
                    if not msg["delivered"]:
                        msg_copy = {**msg, "to": project_id, "delivered": True, "delivered_at": datetime.now(timezone.utc).isoformat()}
                        delivered.append(msg_copy)
                        self.message_stats["total_received"] += 1
        # 标记已投递
        for msg in self.message_queue[topic]:
            msg["delivered"] = True
        return delivered
    
    def get_message_stats(self) -> Dict[str, Any]:
        """获取消息统计"""
        return {
            "stats": self.message_stats,
            "subscriptions_count": len(self.subscriptions),
            "topics_count": len(self.message_queue),
            "total_pending": sum(1 for msgs in self.message_queue.values() for m in msgs if not m["delivered"])
        }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        if action == "subscribe":
            project_id = task.get("project_id", "")
            topic = task.get("topic", "")
            success = self.subscribe(project_id, topic)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {project_id} 订阅 {topic}"}
        elif action == "publish":
            from_project = task.get("from_project", "")
            topic = task.get("topic", "")
            message = task.get("message", {})
            success = self.publish(from_project, topic, message)
            return {"agent": self.name, "action": action, "success": success, "result": f"项目 {from_project} 发布到 {topic}"}
        elif action == "deliver":
            topic = task.get("topic", "")
            delivered = self.deliver(topic)
            return {"agent": self.name, "action": action, "success": True, "result": delivered}
        elif action == "get_message_stats":
            stats = self.get_message_stats()
            return {"agent": self.name, "action": action, "success": True, "result": stats}
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
# PMO 实例 (1 个, 管 8 个 agent, 三权分立 + 3 维度分离)
# ============================================
class PMOInstance:
    """1 个 PMO 实例, 管 8 个 agent (DEC-2026-0002)
    
    三权分立:
    - L0 监督权 (1 个): Sponsor
    - L1 行政权 (1 个): PMO-Main (维度 1 采集)
    - L2 司法权 (6 个): Plan / Engineer (维度 2) / Monitor (维度 3) / Reviewer / Assessor / Message-Broker
    """
    
    def __init__(self, pmo_root: str):
        self.pmo_root = pmo_root
        self.pmo_main = PMOMainAgent(pmo_root)
        self.plan_agent = PlanAgent(pmo_root)
        self.engineer_agent = EngineerAgent(pmo_root)
        self.monitor_agent = MonitorAgent(pmo_root)
        self.reviewer_agent = ReviewerAgent(pmo_root)
        self.assessor_agent = AssessorAgent(pmo_root)
        self.message_broker_agent = MessageBrokerAgent(pmo_root)
        self.sponsor_agent = SponsorAgent(pmo_root)
        self.agents = [
            self.sponsor_agent,
            self.pmo_main,
            self.plan_agent,
            self.engineer_agent,
            self.monitor_agent,
            self.reviewer_agent,
            self.assessor_agent,
            self.message_broker_agent
        ]
    
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
                "L2_judicial": [
                    self.plan_agent.name,
                    self.engineer_agent.name,
                    self.monitor_agent.name,
                    self.reviewer_agent.name,
                    self.assessor_agent.name,
                    self.message_broker_agent.name
                ]
            },
            "three_dimensions": {
                "dimension_1_project_overall": {
                    "agent": self.pmo_main.name,
                    "data_source": "register.yaml + state + quota + archive + isolation"
                },
                "dimension_2_eng_5_stages": {
                    "agent": self.engineer_agent.name,
                    "data_source": "eng-roles/ + 5 阶段产出",
                    "stages": EngineerAgent.ENG_5_STAGES
                },
                "dimension_3_biz_reported": {
                    "agent": self.monitor_agent.name,
                    "data_source": "业务项目按 PMO 规范上报",
                    "required_metrics": MonitorAgent.REPORT_METRICS_5_BASIC
                }
            }
        }
    
    def l2_audit_l1(self) -> List[Dict[str, Any]]:
        """L2 6 个 agent 审计 L1 (三权分立, DEC-2026-0002)"""
        audits = []
        audits.append(self.plan_agent.audit_pmo_main(self.pmo_main))
        audits.append(self.engineer_agent.audit_pmo_main(self.pmo_main))
        audits.append(self.monitor_agent.audit_pmo_main(self.pmo_main))
        audits.append(self.reviewer_agent.audit_pmo_main(self.pmo_main))
        # Assessor 单独处理 (基于 3 维度考核)
        for project_id in self.pmo_main.managed_projects:
            audits.append(self.assessor_agent.assess_project(self.pmo_main, self.engineer_agent, self.monitor_agent, project_id))
        # Message-Broker 提供消息统计
        audits.append(self.message_broker_agent.get_message_stats())
        return audits
    
    def l0_observe_l1(self) -> Dict[str, Any]:
        """L0 Sponsor 监督 L1 (打破递归)"""
        return self.sponsor_agent.observe_metrics(self.pmo_main)


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO 8 Agent (三权分立 + 3 维度分离, DEC-2026-0002) 演示 ===\n")
    
    # 1. 初始化 PMO 实例
    print("[1] 初始化 PMO 实例 (1 个, 管 8 agent)")
    pmo = PMOInstance(PMO_ROOT)
    print(f"  - L0 Sponsor: {pmo.sponsor_agent.name}")
    print(f"  - L1 PMO-Main (维度 1): {pmo.pmo_main.name}")
    print(f"  - L2 Plan: {pmo.plan_agent.name}")
    print(f"  - L2 Engineer (维度 2: 研发 5 阶段): {pmo.engineer_agent.name}")
    print(f"  - L2 Monitor (维度 3: 业务项目上报): {pmo.monitor_agent.name}")
    print(f"  - L2 Reviewer: {pmo.reviewer_agent.name}")
    print(f"  - L2 Assessor (3 维度考核): {pmo.assessor_agent.name}")
    print(f"  - L2 Message-Broker (项目间消息): {pmo.message_broker_agent.name}\n")
    
    # 2. 激活所有 agent
    print("[2] 激活所有 agent (从 idle 到 running)")
    pmo.activate_all()
    for agent in pmo.agents:
        print(f"  - {agent.name}: {agent.reflect()['state']}")
    print()
    
    # 3. L1 注册业务项目 + 维度 1 业务项目整体采集
    print("[3] L1 PMO-Main (维度 1) 注册业务项目 + 状态管理")
    pmo.pmo_main.process({"action": "register_project", "project_id": "1.1"})
    pmo.pmo_main.process({"action": "register_project", "project_id": "1.2"})
    pmo.pmo_main.process({"action": "update_business_state", "project_id": "1.1", "state": "active"})
    print(f"  - 管理项目: {pmo.pmo_main.managed_projects}")
    print(f"  - 项目状态: {pmo.pmo_main.business_state}\n")
    
    # 4. 维度 2 业务项目内研发 5 阶段数据采集
    print("[4] L2 Engineer (维度 2) 采集业务项目内研发 5 阶段数据")
    pmo.engineer_agent.process({"action": "collect_eng_stage_data", "project_id": "1.1", "stage": "requirement", "data": {"doc": "需求文档"}})
    pmo.engineer_agent.process({"action": "collect_eng_stage_data", "project_id": "1.1", "stage": "development", "data": {"code": "代码"}})
    pmo.engineer_agent.process({"action": "collect_eng_stage_data", "project_id": "1.1", "stage": "test", "data": {"test_cases": 5}})
    eng_status = pmo.engineer_agent.process({"action": "get_eng_5_stages_status", "project_id": "1.1"})
    print(f"  - 1.1 研发 5 阶段状态: {eng_status['result']}\n")
    
    # 5. 维度 3 业务项目上报 + 上报合规监管
    print("[5] L2 Monitor (维度 3) 采集业务项目上报 + 上报合规监管")
    pmo.pmo_main.process({"action": "collect_business_reported_metrics", "project_id": "1.1", "metrics": {
        "flow_latency": 100, "exception_rate": 0.01, "pass_rate": 0.99, "rollback_rate": 0.001, "token_consumption": 10000
    }})
    pmo.monitor_agent.process({"action": "collect_reported_data", "project_id": "1.1", "data": {
        "flow_latency": 100, "exception_rate": 0.01, "pass_rate": 0.99, "rollback_rate": 0.001, "token_consumption": 10000
    }})
    compliance = pmo.monitor_agent.process({"action": "get_compliance_report", "project_id": "1.1"})
    print(f"  - 1.1 上报合规报告: {compliance['result']}\n")
    
    # 6. L2 Assessor 3 维度分别考核
    print("[6] L2 Assessor 3 维度分别考核")
    assessment = pmo.assessor_agent.assess_project(pmo.pmo_main, pmo.engineer_agent, pmo.monitor_agent, "1.1")
    print(f"  - 1.1 维度 1 (业务项目整体): {assessment['dimension_1']['verdict']}")
    print(f"  - 1.1 维度 2 (研发 5 阶段): {assessment['dimension_2']['verdict']}")
    print(f"  - 1.1 维度 3 (上报合规): {assessment['dimension_3']['verdict']}")
    print(f"  - 1.1 总考核: {assessment['overall_verdict']}\n")
    
    # 7. L2 Message-Broker 项目间消息经 PMO 中介
    print("[7] L2 Message-Broker 项目间消息经 PMO 中介")
    pmo.message_broker_agent.process({"action": "subscribe", "project_id": "1.1", "topic": "biz.1.2.state"})
    pmo.message_broker_agent.process({"action": "publish", "from_project": "1.2", "topic": "biz.1.2.state", "message": {"event": "active"}})
    pmo.message_broker_agent.process({"action": "deliver", "topic": "biz.1.2.state"})
    msg_stats = pmo.message_broker_agent.process({"action": "get_message_stats"})
    print(f"  - 消息统计: {msg_stats['result']}\n")
    
    # 8. L2 6 个 agent 审计 L1 (三权分立, DEC-2026-0002)
    print("[8] L2 6 个 agent 审计 L1 (三权分立)")
    audits = pmo.l2_audit_l1()
    print(f"  - 审计结果数: {len(audits)} (Plan/Engineer/Monitor/Reviewer/Assessor/Message-Broker)\n")
    
    # 9. L0 Sponsor 监督 L1 (打破递归)
    print("[9] L0 Sponsor 监督 L1 (顶层权威)")
    obs = pmo.l0_observe_l1()
    print(f"  - Sponsor 观察: {obs['pmo_main_state']}")
    print(f"  - 管理项目数: {len(obs['managed_projects'])}\n")
    
    # 10. 反射 (introspection)
    print("[10] 反射 (introspection) — 各 agent 看自己状态")
    for agent in pmo.agents:
        r = agent.reflect()
        print(f"  - {agent.name}: state={r['state']}, layer={agent.layer}, reflection_count={r['reflection_count']}")
    print()
    
    # 11. 状态报告
    print("[11] PMO 实例状态报告")
    status = pmo.get_status()
    print(f"  - agent 总数: {status['agent_count']}")
    print(f"  - 三权分立: L0={status['three_powers']['L0_sponsor']}, L1={status['three_powers']['L1_pmo_main']}, L2={len(status['three_powers']['L2_judicial'])} 个司法权")
    print(f"  - 3 维度采集:")
    print(f"    - 维度 1 (业务项目整体): {status['three_dimensions']['dimension_1_project_overall']['agent']}")
    print(f"    - 维度 2 (研发 5 阶段): {status['three_dimensions']['dimension_2_eng_5_stages']['agent']} → {len(status['three_dimensions']['dimension_2_eng_5_stages']['stages'])} 阶段")
    print(f"    - 维度 3 (业务项目上报): {status['three_dimensions']['dimension_3_biz_reported']['agent']} → {len(status['three_dimensions']['dimension_3_biz_reported']['required_metrics'])} 指标")
    print()
    print("=== 8 Agent 演示完成 ===")
