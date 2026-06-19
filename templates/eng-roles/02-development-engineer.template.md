# 02-development-engineer.template.md (PMO 给业务项目参考)

**业务项目从此模板复制, 然后按业务调整实施**

## 元信息

- **阶段名**: Development-Engineer (研发)
- **必选**: **是 (必选, 不可关闭)**
- **元规则**: 0.0.13
- **PMO 监管**: L2 PMO-Engineer-Agent (维度 2 采上报数据)

## 输入 (PMO 规范)

- `requirements_doc`: 需求文档
- `tech_specs`: 技术规范
- `architecture_diagram`: 架构图

## 输出 (PMO 规范)

- `code_artifacts`: 代码产物
- `api_documentation`: API 文档
- `database_schema`: 数据库 schema
- `pm0_decision_log`: 决策日志 (PMO 7 项合规)

## 责任 (业务项目可调)

- 写代码
- 工程实现
- Code Review

**业务项目可加业务特定责任** (如: 量化策略代码 / 推荐算法实现)

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
02-development-engineer.py
业务项目内 研发阶段 agent (必选)
业务项目从此模板复制, 然后按业务调整
"""

from typing import Dict, List, Any


class DevelopmentEngineer:
    """研发阶段 agent (业务项目实施, 必选)"""

    def __init__(self, biz_project_id: str, config: Dict = None):
        self.biz_project_id = biz_project_id
        self.config = config or {}
        self.pmo_compliance_version = "0.0.13"

    def define_inputs(self) -> List[str]:
        """PMO 规范输入字段"""
        return ["requirements_doc", "tech_specs", "architecture_diagram"]

    def define_outputs(self) -> List[str]:
        """PMO 规范输出字段"""
        return ["code_artifacts", "api_documentation", "database_schema", "pm0_decision_log"]

    def execute(self, inputs: Dict) -> Dict:
        """业务项目具体实现研发阶段任务"""
        # 业务项目按业务场景实现
        return {
            "code_artifacts": "...",
            "api_documentation": "...",
            "database_schema": "...",
            "pm0_decision_log": "..."
        }

    def report_to_pmo(self) -> Dict:
        """上报 PMO (PMO 监督用)"""
        return {
            "biz_project_id": self.biz_project_id,
            "stage": "development",
            "pmo_7_compliance": 7,
            "status": "completed",
            "artifacts": self.execute({})
        }
```

## 业务项目调整建议

- **不可关闭**: 研发阶段是必选, 业务项目**必须**实施
- **扩展**: 业务项目可加业务特定输入输出 (如: `quant_strategy_code` / `recommendation_model`)
- **业务特定工具**: 业务项目可加业务特定工具 (如: 量化回测工具 / 推荐算法库)
- **改名**: 业务项目可改 agent 名字 (如: Quant-Engineer / Recommendation-Engineer)
- **业务特定语言**: 业务项目可换语言 (如: Python → Go / Rust)

**但必须**:
- 输入输出字段**保留** PMO 规范字段
- PMO 7 项合规**全部**通过
- 研发阶段**不可关闭**

## 关键

- **PMO 给模板, 业务项目实施**
- **必选, 不可关闭**
- **可扩展业务特定工具**
- **业务项目上报 PMO 监督**
