"""
01-requirement-engineer.py
业务项目 1.1-pmo-self 需求阶段 agent
业务项目从 PMO/templates/eng-roles/01-requirement-engineer.template.md 复制 + 调整实施
元规则: 0.0.13 (DEC-2026-0003)
"""

from typing import Dict, List, Any


class RequirementEngineer:
    """需求阶段 agent (业务项目 1.1-pmo-self 实施)"""

    def __init__(self, biz_project_id: str = "1.1-pmo-self", config: Dict = None):
        self.biz_project_id = biz_project_id
        self.config = config or {}
        self.pmo_compliance_version = "0.0.13"
        self.stage = "requirement"
        self.enabled = True

    def define_inputs(self) -> List[str]:
        """PMO 规范输入字段"""
        return ["business_objective", "user_stories", "acceptance_criteria"]

    def define_outputs(self) -> List[str]:
        """PMO 规范输出字段"""
        return ["requirements_doc", "requirement_traceability", "pm0_decision_log"]

    def execute(self, inputs: Dict) -> Dict:
        """业务项目 1.1-pmo-self 实现需求阶段任务 (PMO 自建项目的需求)"""
        return {
            "requirements_doc": {
                "title": "PMO 自建项目需求",
                "objectives": inputs.get("business_objective", []),
                "user_stories": inputs.get("user_stories", []),
                "acceptance_criteria": inputs.get("acceptance_criteria", [])
            },
            "requirement_traceability": {
                "trace_id": "REQ-001",
                "linked_user_stories": ["US-1", "US-2"]
            },
            "pm0_decision_log": {
                "decision": "PMO 自建项目需求确定",
                "rationale": "Sponsor 推动 PMO 1 套规范 + N 项目",
                "timestamp": "2026-06-19"
            }
        }

    def report_to_pmo(self) -> Dict:
        """上报 PMO (PMO 监督用)"""
        return {
            "biz_project_id": self.biz_project_id,
            "stage": self.stage,
            "pmo_7_compliance": 7,
            "status": "completed",
            "artifacts": self.execute({})
        }


if __name__ == "__main__":
    agent = RequirementEngineer()
    print(f"Stage: {agent.stage}")
    print(f"Inputs: {agent.define_inputs()}")
    print(f"Outputs: {agent.define_outputs()}")
    print(f"Report: {agent.report_to_pmo()}")
