# 运行时 (Runtime, m0.2)

**PMO 运行时 v0.2.1** — 8 agent 三权分立 + 3 维度分离 (DEC-2026-0002)

## 8 Agent (三权分立 + 3 维度分离)

### L0 监督权 (1 个)
- **Sponsor** — 人机协作, 看指标看板, 不执行

### L1 行政权 (1 个)
- **PMO-Main** — 1 实例管 N 项目
  - **数据维度**: 维度 1 (业务项目整体: 注册/状态/配额/归档/隔离)

### L2 司法权 (6 个)
- **Plan-Agent** — 计划/治理
- **Engineer-Agent** — 维度 2 采集
  - **数据维度**: 维度 2 (业务项目内研发 5 阶段: 需求/研发/测试/运维/评估)
- **Monitor-Agent** — 维度 3 采集
  - **数据维度**: 维度 3 (业务项目上报: 5 项基础 + 3 项合规)
- **Reviewer-Agent** — 审查/审计
- **Assessor-Agent** — 3 维度分别考核
  - 考核业务项目整体 (m2.6 7 项)
  - 考核业务项目内研发 5 阶段 (PMO 7 项)
  - 考核业务项目内业务上报合规 (PMO 规范)
- **Message-Broker-Agent** — 项目间消息
  - 业务项目↔业务项目消息经 PMO 实例中介

## 3 维度架构 (DEC-2026-0002)

| 维度 | 数据源 | 谁采 | 谁存 |
|---|---|---|---|
| **维度 1**: 业务项目整体 | register + state + quota + archive + isolation | L1 PMO-Main | PMO 存 |
| **维度 2**: 研发 5 阶段 | eng-roles + 5 阶段产出 | L2 Engineer-Agent | PMO 存上报 + 业务项目存全量 |
| **维度 3**: 业务项目上报 | 业务项目按 PMO 规范上报的 5 项基础 | L2 Monitor-Agent | 业务项目存业务 + PMO 存上报 |

## 业务项目 2 层合规

- **业务项目整体** (维度 1) → 业务项目整体契约 → 业务项目被 PMO 考核
- **业务项目内研发 5 阶段** (维度 2) → 研发 5 阶段契约 → 研发 5 阶段被 PMO 考核
- **业务项目内业务** (业务项目自管) → 业务项目自维护业务 agent / 业务流程 / 业务异常 / 业务指标
- **业务项目上报** (维度 3) → 业务项目按 PMO 规范上报关键指标 → PMO 监管上报合规

## 文件结构

```
scripts/runtime/
├── pmo_runtime.py          # 主入口
├── core/
│   ├── state_machine.py    # 状态机 (业务项目 / 任务 / agent / 阶段门控)
│   └── reflect.py          # 反射 (introspection, 0.0.8 自进化)
├── agents/
│   └── agent_base.py       # 8 PMO agent (三权分立 + 3 维度分离)
├── triggers/
│   └── triggers.py         # 4 类触发器 (时间/事件/状态/手动)
├── exceptions/
│   └── exceptions.py       # 3 层异常拦截 (L0/L1/L2)
├── protocol/
│   └── protocol.py         # 通信协议 (agent↔agent, agent↔业务, 业务↔业务 经 PMO)
├── notify/
│   └── notify.py           # Sponsor 通知 (3 层: 简报/看板/即时)
├── metrics/
│   └── metrics.py          # 指标跑批 (业务/治理/工程 3 类)
└── perf_benchmark.py       # 性能基准
```

## 启动

```bash
cd /Users/sylvieshu/Desktop/AI\ finance\ 哈吉米/PMO
python3 scripts/runtime/pmo_runtime.py
```

## 关键决策

- **DEC-2026-0002**: 14 块关键调整 (2026-06-18)
- **m0.2 v0.2.1**: 5 agent → 8 agent (加 Monitor/Assessor/Message-Broker)
- **3 维度架构**: 业务项目整体 / 研发 5 阶段 / 业务项目上报
- **2 层合规**: 业务项目整体 + 业务项目内研发
- **3 层上报**: 业务自采 + 业务上报 + PMO 存上报
- **3 维度考核**: Assessor 按 3 维度分别考核
