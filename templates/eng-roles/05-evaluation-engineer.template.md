# 05-evaluation-engineer.template.md (PMO 给业务项目参考)

**业务项目从此模板复制, 然后按业务调整实施**

## 元信息

- **阶段名**: Evaluation-Engineer (评估)
- **必选**: 否 (业务项目可关闭)
- **元规则**: 0.0.13
- **PMO 监管**: L2 PMO-Engineer-Agent (维度 2 采上报数据)

## 输入 (PMO 规范)

- `all_stage_outputs`: 所有阶段产出
- `business_metrics`: 业务指标
- `performance_data`: 性能数据

## 输出 (PMO 规范)

- `evaluation_report`: 评估报告
- `lessons_learned`: 经验教训
- `self_evolution_proposal`: 自进化提案
- `pm0_decision_log`: 决策日志 (PMO 7 项合规)
- `sponsor_report`: Sponsor 报告

## 责任 (业务项目可调)

- 业务评估
- 性能评估
- 复盘

**业务项目可加业务特定责任** (如: 夏普比率/最大回撤评估 / 推荐点击率评估 / 内容质量评估)

## PMO 7 项合规 (不可减少)

- [ ] 阶段门控 (m1.3)
- [ ] 决策日志 (m1.1) — **重点**: 自进化决策
- [ ] 不可变文档 (m0.1)
- [ ] 异常拦截 (m0.4)
- [ ] 指标可贯彻 (m1.2) — **重点**: 业务指标可贯彻
- [ ] 3 层告警 (m0.4)
- [ ] Sponsor 报告 (m1.5) — **重点**: 自进化提案
- [ ] 自进化 (0.0.8) — 评估特有

**业务项目可加业务特定合规项** (PMO 7 项不可减少)

## 业务项目实施 (Python 模板)

```python
"""
05-evaluation-engineer.py
业务项目内 评估阶段 agent
业务项目从此模板复制, 然后按业务调整
"""

from typing import Dict, List, Any


class EvaluationEngineer:
    """评估阶段 agent (业务项目实施)"""

    def __init__(self, biz_project_id: str, config: Dict = None):
        self.biz_project_id = biz_project_id
        self.config = config or {}
        self.pmo_compliance_version = "0.0.13"

    def define_inputs(self) -> List[str]:
        """PMO 规范输入字段"""
        return ["all_stage_outputs", "business_metrics", "performance_data"]

    def define_outputs(self) -> List[str]:
        """PMO 规范输出字段"""
        return ["evaluation_report", "lessons_learned", "self_evolution_proposal", "pm0_decision_log", "sponsor_report"]

    def execute(self, inputs: Dict) -> Dict:
        """业务项目具体实现评估阶段任务"""
        # 业务项目按业务场景实现
        return {
            "evaluation_report": "...",
            "lessons_learned": "...",
            "self_evolution_proposal": "...",
            "pm0_decision_log": "...",
            "sponsor_report": "..."
        }

    def report_to_pmo(self) -> Dict:
        """上报 PMO (PMO 监督用)"""
        return {
            "biz_project_id": self.biz_project_id,
            "stage": "evaluation",
            "pmo_7_compliance": 7,
            "status": "completed",
            "artifacts": self.execute({})
        }
```

## 业务项目调整建议

- **简化**: 业务项目可关闭评估阶段 (在 `register.yaml` 设 `enabled: false`)
- **扩展**: 业务项目可加业务特定评估指标 (如: `sharpe_ratio` / `max_drawdown` / `click_through_rate`)
- **业务特定工具**: 业务项目可加业务特定工具 (如: 风控分析工具 / 推荐 AB 评估工具)
- **改名**: 业务项目可改 agent 名字 (如: Quant-Evaluation-Engineer / Recommendation-Evaluation-Engineer)

**但必须**:
- 输入输出字段**保留** PMO 规范字段
- PMO 7 项合规**全部**通过
- 可选阶段可关闭, 但如实施必须有 `self_evolution_proposal` (自进化提案)
- 必须有 `sponsor_report` (Sponsor 报告)

## 关键

- **PMO 给模板, 业务项目实施**
- **可选, 业务项目可关闭**
- **可扩展业务特定评估指标**
- **如实施必须有自进化提案 + Sponsor 报告**
- **业务项目上报 PMO 监督**
