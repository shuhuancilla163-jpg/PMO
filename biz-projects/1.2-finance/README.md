# 业务项目 1.2-finance (量化金融业务项目)

**业务项目 1.2-finance 接入 PMO 实例演示** (DEC-2026-0003 5 阶段修正后)

## 项目概述

- **业务项目 ID**: 1.2-finance
- **业务项目名称**: 量化金融业务项目
- **业务项目类型**: finance-quant
- **业务场景**: 量化金融 (策略研究/回测/风控/组合管理/合规/报告)
- **Sponsor**: Sponsor
- **注册时间**: 2026-06-19
- **状态**: active

## 业务项目结构 (DEC-2026-0003)

```
biz-projects/1.2-finance/
├── README.md
├── register.yaml              # 业务项目注册
├── eng-roles/                 # 5 阶段研发 agent (PMO 监管, 0.0.13)
│   ├── 01-requirement-engineer.py
│   ├── 02-development-engineer.py
│   ├── 03-test-engineer.py
│   ├── 04-operations-engineer.py
│   ├── 05-evaluation-engineer.py
│   ├── register.yaml
│   └── README.md
├── biz-agents/                # 业务需求运营 agent (业务自管, 0.0.14)
│   ├── 01-data-engineer.py    # 业务 agent 1: 数据工程
│   ├── 02-quant-analyst.py    # 业务 agent 2: 量化分析
│   ├── 03-risk-manager.py     # 业务 agent 3: 风控
│   ├── 04-portfolio-mgr.py    # 业务 agent 4: 组合管理
│   ├── 05-compliance-officer.py  # 业务 agent 5: 合规
│   ├── 06-reporting-analyst.py   # 业务 agent 6: 报告
│   └── README.md
├── reports/                   # 5 阶段上报 (PMO 采集源)
│   ├── dev-report.yaml
│   ├── test-report.yaml
│   └── ops-report.yaml
└── biz-data/                  # 业务数据 (业务自存, PMO 不存)
```

## 业务项目 2 类 agent (DEC-2026-0003)

### 1. eng-roles/ — 5 阶段研发 agent (PMO 监管)
- 物理位置: `eng-roles/`
- 数量: 5 个 (或简化 2-3 个)
- 实施: 业务项目从 `PMO/templates/eng-roles/` 复制 + 调整
- PMO 监督: 7 项合规 (阶段门控/决策日志/不可变文档/异常拦截/指标可贯彻/3 层告警/Sponsor 报告)
- 元规则: 0.0.13

### 2. biz-agents/ — 业务需求运营 agent (业务自管)
- 物理位置: `biz-agents/`
- 数量: **6 个 (业务项目自定, 不固定 8)**
- 实施: 业务项目完全自定
- PMO 监督: **不监督内容**
- 元规则: 0.0.14

## 业务 agent 清单 (6 个, 业务项目自定)

| # | 业务 agent | 责任 | 业务场景 |
|---|---|---|---|
| 1 | Data-Engineer | 金融数据采集/清洗/存储 | 金融数据 ETL |
| 2 | Quant-Analyst | 量化策略研究/回测 | 量化策略 |
| 3 | Risk-Manager | 风险监控/预警 | 风控 |
| 4 | Portfolio-Manager | 组合管理/调仓 | 组合管理 |
| 5 | Compliance-Officer | 合规检查/审计 | 合规 |
| 6 | Reporting-Analyst | 业务报告/可视化 | 报告 |

## 业务项目 2 层合规 (0.0.11)

### 第 1 层: 业务项目整体 (m2.6 7 项, PMO 监管)
- 业务项目注册 ✓
- 业务项目状态机 (active) ✓
- 业务项目配额 4 维 ✓
- 业务项目归档 4 层面 ✓
- 业务项目隔离 3 维 ✓
- 业务项目告警 3 层 ✓
- 业务项目 checklist 6+3 项 ✓

### 第 2 层: 业务项目内研发 5 阶段 (0.0.13, PMO 监管)
- Requirement-Engineer (可选) ✓
- Development-Engineer (必选) ✓
- Test-Engineer (必选) ✓
- Operations-Engineer (必选) ✓
- Evaluation-Engineer (可选) ✓

### 第 3 层: 业务需求运营 agent (0.0.14, 业务自管)
- Data-Engineer (业务自定) ✓
- Quant-Analyst (业务自定) ✓
- Risk-Manager (业务自定) ✓
- Portfolio-Manager (业务自定) ✓
- Compliance-Officer (业务自定) ✓
- Reporting-Analyst (业务自定) ✓

## 业务项目接入 PMO 5 步流程

1. 业务项目注册 (m2.6) — register.yaml + 签 3 份契约 ✓
2. 业务项目内研发 5 阶段实施 — eng-roles/ 从 PMO 模板复制 + 调整 ✓
3. 业务项目内业务 agent 自定 — biz-agents/ 业务项目自定 6 个 ✓
4. 业务项目接入 PMO 消息机制 — messaging.yaml ✓
5. 业务项目接入 PMO 监管 — reports/ 上报 5 阶段 ✓

## 关键 (DEC-2026-0003)

- **5 阶段 agent 物理位置在业务项目内** (eng-roles/)
- **业务需求运营 agent 业务项目自定** (biz-agents/, 6 个演示)
- **PMO 不实施 5 阶段 agent, 只给模板 + 规范 + 监督**
- **PMO 不干预业务 agent 内容**
- **业务项目自管业务数据** (biz-data/, PMO 不存)

## 关键决策

- **DEC-2026-0002**: 业务项目 2 层合规 + 8 PMO 角色 + 3 维度架构
- **DEC-2026-0003**: 5 阶段 agent 物理位置业务项目内
