# 01-requirement-engineer.template.md (PMO 给业务项目参考)

**业务项目从此模板复制, 然后按业务调整实施**

## 元信息

- **阶段名**: Requirement-Engineer (需求)
- **必选**: 否 (业务项目可关闭)
- **元规则**: 0.0.13
- **PMO 监管**: L2 PMO-Engineer-Agent (维度 2 采上报数据)

## 输入 (PMO 规范)

- `business_objective`: 业务目标
- `user_stories`: 用户故事
- `acceptance_criteria`: 验收标准

## 输出 (PMO 规范)

- `requirements_doc`: 需求文档
- `requirement_traceability`: 需求追溯矩阵
- `pm0_decision_log`: 决策日志 (PMO 7 项合规)

## 责任 (业务项目可调)

- 业务需求调研
- 业务需求分析
- 业务需求扩展

**业务项目可加业务特定责任** (如: 业务建模 / 业务场景细化)

## PMO 7 项合规 (不可减少)

- [ ] 阶段门控 (m1.3)
- [ ] 决策日志 (m1.1)
- [ ] 不可变文档 (m0.1)
- [ ] 异常拦截 (m0.4)
- [ ] 指标可贯彻 (m1.2)
- [ ] 3 层告警 (m0.4)
- [ ] Sponsor 报告 (m1.5)

**业务项目可加业务特定合规项** (PMO 7 项不可减少)

## 业务项目实施 (Python 模板)

```python
"""
01-requirement-engineer.py
业务项目内 需求阶段 agent
业务项目从此模板复制, 然后按业务调整
"""

from typing import Dict, List, Any


class RequirementEngineer:
    """需求阶段 agent (业务项目实施)"""

    def __init__(self, biz_project_id: str, config: Dict = None):
        self.biz_project_id = biz_project_id
        self.config = config or {}
        self.pmo_compliance_version = "0.0.13"

    def define_inputs(self) -> List[str]:
        """PMO 规范输入字段"""
        return ["business_objective", "user_stories", "acceptance_criteria"]

    def define_outputs(self) -> List[str]:
        """PMO 规范输出字段"""
        return ["requirements_doc", "requirement_traceability", "pm0_decision_log"]

    def execute(self, inputs: Dict) -> Dict:
        """业务项目具体实现需求阶段任务"""
        # 业务项目按业务场景实现
        return {
            "requirements_doc": "...",
            "requirement_traceability": "...",
            "pm0_decision_log": "..."
        }

    def report_to_pmo(self) -> Dict:
        """上报 PMO (PMO 监督用)"""
        return {
            "biz_project_id": self.biz_project_id,
            "stage": "requirement",
            "pmo_7_compliance": 7,
            "status": "completed",
            "artifacts": self.execute({})
        }
```

## 业务项目调整建议

- **简化**: 业务项目可关闭需求阶段 (在 `register.yaml` 设 `enabled: false`)
- **扩展**: 业务项目可加业务特定输入输出 (如: `business_modeling_doc`)
- **业务特定工具**: 业务项目可加业务特定工具 (如: 金融建模工具)
- **改名**: 业务项目可改 agent 名字 (如: Quant-Requirement-Engineer)

**但必须**:
- 输入输出字段**保留** PMO 规范字段
- PMO 7 项合规**全部**通过
- 必选字段不可关闭

## 关键

- **PMO 给模板, 业务项目实施**
- **可调但不可减 PMO 7 项**
- **可简化可扩展但必选字段保留**
- **业务项目上报 PMO 监督**
