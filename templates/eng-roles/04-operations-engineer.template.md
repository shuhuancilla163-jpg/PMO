# 04-operations-engineer.template.md (PMO 给业务项目参考)

**业务项目从此模板复制, 然后按业务调整实施**

## 元信息

- **阶段名**: Operations-Engineer (运维)
- **必选**: **是 (必选, 不可关闭)**
- **元规则**: 0.0.13
- **PMO 监管**: L2 PMO-Engineer-Agent (维度 2 采上报数据)

## 输入 (PMO 规范)

- `code_artifacts`: 代码产物
- `deployment_plan`: 部署计划
- `monitoring_specs`: 监控规范

## 输出 (PMO 规范)

- `deployment_report`: 部署报告
- `monitoring_dashboard`: 监控面板
- `disaster_recovery_plan`: 灾备方案
- `pm0_decision_log`: 决策日志 (PMO 7 项合规)

## 责任 (业务项目可调)

- 部署
- CI/CD
- 监控
- 灾备

**业务项目可加业务特定责任** (如: 金融数据灾备 / 推荐服务扩缩容 / 内容审核 SLA)

## PMO 7 项合规 (不可减少)

- [ ] 阶段门控 (m1.3)
- [ ] 决策日志 (m1.1)
- [ ] 不可变文档 (m0.1)
- [ ] 异常拦截 (m0.4) — **重点**: 异常拦截率
- [ ] 指标可贯彻 (m1.2)
- [ ] 3 层告警 (m0.4) — **重点**: 告警通道
- [ ] Sponsor 报告 (m1.5) — **重点**: 灾备
- [ ] 灾备 (m0.4) — 运维特有

**业务项目可加业务特定合规项** (PMO 7 项不可减少)

## 业务项目实施 (Python 模板)

```python
"""
04-operations-engineer.py
业务项目内 运维阶段 agent (必选)
业务项目从此模板复制, 然后按业务调整
"""

from typing import Dict, List, Any


class OperationsEngineer:
    """运维阶段 agent (业务项目实施, 必选)"""

    def __init__(self, biz_project_id: str, config: Dict = None):
        self.biz_project_id = biz_project_id
        self.config = config or {}
        self.pmo_compliance_version = "0.0.13"

    def define_inputs(self) -> List[str]:
        """PMO 规范输入字段"""
        return ["code_artifacts", "deployment_plan", "monitoring_specs"]

    def define_outputs(self) -> List[str]:
        """PMO 规范输出字段"""
        return ["deployment_report", "monitoring_dashboard", "disaster_recovery_plan", "pm0_decision_log"]

    def execute(self, inputs: Dict) -> Dict:
        """业务项目具体实现运维阶段任务"""
        # 业务项目按业务场景实现
        return {
            "deployment_report": "...",
            "monitoring_dashboard": "...",
            "disaster_recovery_plan": "...",
            "pm0_decision_log": "..."
        }

    def report_to_pmo(self) -> Dict:
        """上报 PMO (PMO 监督用)"""
        return {
            "biz_project_id": self.biz_project_id,
            "stage": "operations",
            "pmo_7_compliance": 7,
            "status": "completed",
            "artifacts": self.execute({})
        }
```

## 业务项目调整建议

- **不可关闭**: 运维阶段是必选, 业务项目**必须**实施
- **扩展**: 业务项目可加业务特定运维场景 (如: 金融数据灾备 / 推荐服务扩缩容)
- **业务特定工具**: 业务项目可加业务特定工具 (如: Kubernetes / Docker / Terraform)
- **改名**: 业务项目可改 agent 名字 (如: Quant-Ops-Engineer / Recommendation-Ops-Engineer)

**但必须**:
- 输入输出字段**保留** PMO 规范字段
- PMO 7 项合规**全部**通过
- 运维阶段**不可关闭**
- 必须有 `disaster_recovery_plan` (灾备方案)
- 必须有 `monitoring_dashboard` (监控面板)

## 关键

- **PMO 给模板, 业务项目实施**
- **必选, 不可关闭**
- **可扩展业务特定运维场景**
- **必须灾备方案 + 监控面板**
- **业务项目上报 PMO 监督**
