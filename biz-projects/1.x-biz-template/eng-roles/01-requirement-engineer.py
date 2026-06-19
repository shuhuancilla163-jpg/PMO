"""
01-requirement-engineer.py
业务项目 1.2-finance 需求阶段 agent
业务项目从 PMO/templates/eng-roles/01-requirement-engineer.template.md 复制 + 业务调整
元规则: 0.0.13 (DEC-2026-0003)
业务场景: 量化金融
"""

from typing import Dict, List, Any


class RequirementEngineer:
    """需求阶段 agent (业务项目 1.2-finance 实施)"""

    def __init__(self, biz_project_id: str = "1.2-finance", config: Dict = None):
        self.biz_project_id = biz_project_id
        self.config = config or {}
        self.pmo_compliance_version = "0.0.13"
        self.stage = "requirement"
        self.enabled = True

    def define_inputs(self) -> List[str]:
        """PMO 规范输入 + 业务项目扩展"""
        # PMO 规范字段 (不可减少)
        pmo_inputs = ["business_objective", "user_stories", "acceptance_criteria"]
        # 业务项目扩展 (业务特定)
        biz_specific = ["financial_markets", "trading_strategies", "risk_constraints"]
        return pmo_inputs + biz_specific

    def define_outputs(self) -> List[str]:
        """PMO 规范输出 + 业务项目扩展"""
        # PMO 规范字段 (不可减少)
        pmo_outputs = ["requirements_doc", "requirement_traceability", "pm0_decision_log"]
        # 业务项目扩展 (业务特定)
        biz_specific = ["quant_strategy_spec", "risk_policy_doc"]
        return pmo_outputs + biz_specific

    def execute(self, inputs: Dict) -> Dict:
        """业务项目 1.2-finance 实现需求阶段任务 (量化金融需求)"""
        return {
            "requirements_doc": {
                "title": "量化金融业务项目需求",
                "objectives": ["实现量化策略回测", "实现实时风控", "实现组合优化"],
                "user_stories": ["US-1: 数据 ETL", "US-2: 策略回测", "US-3: 实时风控"],
                "acceptance_criteria": ["回测夏普比率 > 1.5", "风控延迟 < 100ms"]
            },
            "requirement_traceability": {
                "trace_id": "FIN-REQ-001",
                "linked_user_stories": ["US-1", "US-2", "US-3"]
            },
            "quant_strategy_spec": {
                "strategies": ["mean_reversion", "momentum", "arbitrage"],
                "instruments": ["stocks", "futures", "options"],
                "frequency": "intraday"
            },
            "risk_policy_doc": {
                "max_position": "10% per stock",
                "max_drawdown": "15%",
                "stop_loss": "5%"
            },
            "pm0_decision_log": {
                "decision": "量化金融业务项目需求确定",
                "rationale": "Sponsor 推动 AI 金融场景",
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
