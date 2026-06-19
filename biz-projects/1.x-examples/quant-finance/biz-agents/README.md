# 业务项目 1.2-finance biz-agents/

**业务项目 1.2-finance 业务需求运营 agent** (DEC-2026-0003, 0.0.14 业务项目自定原则)

**关键**:
- 业务需求运营 agent **完全由业务项目自定** (数量/名字/责任/输入输出)
- PMO **不预设不干预** (不固定 8 个)
- PMO **不监管业务 agent 内容**

## 6 业务 agent 清单 (业务项目自定)

业务项目 1.2-finance 自定 **6 个业务 agent** (演示, 业务项目可调, 不固定 8):

| # | 业务 agent | 责任 | 业务场景 |
|---|---|---|---|
| 1 | Data-Engineer | 金融数据 ETL (采集/清洗/存储) | 金融数据 |
| 2 | Quant-Analyst | 量化策略研究/回测 | 量化策略 |
| 3 | Risk-Manager | 风险监控/预警 | 风控 |
| 4 | Portfolio-Manager | 组合管理/调仓 | 组合管理 |
| 5 | Compliance-Officer | 合规检查/审计 | 合规 |
| 6 | Reporting-Analyst | 业务报告/可视化 | 报告 |

## 业务 agent 元规则 (0.0.14)

**业务项目可自定** (PMO 不干预):
- 数量 (演示 6 个, 业务项目可调)
- 名字 (如: Data-Engineer / Quant-Analyst)
- 责任
- 输入输出
- 实现语言/框架
- 业务场景

**PMO 不要求**:
- PMO 7 项合规 (业务 agent 不需要)
- 决策日志 (业务 agent 不需要)
- 不可变文档 (业务 agent 不需要)
- 异常拦截 (业务 agent 自管业务异常)
- 指标可贯彻 (业务指标业务自管)
- 3 层告警 (业务告警业务自管)
- Sponsor 报告 (业务 agent 不需要)

## PMO 监督边界

PMO **不监督**:
- 业务 agent 具体实现代码
- 业务 agent 业务逻辑
- 业务 agent 业务数据
- 业务 agent 数量/名字
- 业务 agent 责任/输入输出

PMO **只监督**:
- 业务项目整体 m2.6 7 项合规
- 业务项目 5 阶段 agent (eng-roles/) 0.0.13 合规
- **不**监督业务 agent (biz-agents/) 内容

## 业务 agent 与 5 阶段 agent 区别

| 维度 | 5 阶段 agent (eng-roles/) | 业务 agent (biz-agents/) |
|---|---|---|
| 物理位置 | eng-roles/ | biz-agents/ |
| 数量 | 5 个 (或简化 2-3) | **6 个 (业务项目自定)** |
| 命名 | PMO 规范 (Requirement-Engineer 等) | **业务项目自定 (Data-Engineer 等)** |
| 实施 | 业务项目从 PMO 模板复制 + 调整 | 业务项目完全自定 |
| PMO 7 项合规 | **必选** | **不要求** |
| PMO 监督 | **监管** | **不监管** |
| 元规则 | 0.0.13 | **0.0.14 (本目录)** |

## 业务数据 (业务项目自存, PMO 不存)

业务数据存于 `biz-projects/1.2-finance/biz-data/`:
- 市场数据 / 交易数据 / 持仓数据
- 业务指标 / 风险指标 / 合规日志
- **PMO 不存业务数据** (业务自管)

## 关键 (DEC-2026-0003)

- **业务需求运营 agent 完全由业务项目自定**
- **PMO 不预设** 业务 agent 数量/名字/责任/输入输出
- **PMO 不干预** 业务 agent 内容
- **业务 agent 不需要 PMO 7 项合规**
- **业务 agent 数量业务项目自定** (演示 6 个, 不固定 8)
