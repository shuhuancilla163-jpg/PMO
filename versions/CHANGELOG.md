# Changelog (PMO 平台变更日志)

所有重要变更记录在这里 (含规范演进, 业务接入, 重大决策)。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [0.2.2] - 2026-06-19

### Added (m0.2 v0.2.1, DEC-2026-0002 实施)
- 8 PMO 角色 (从 5 → 8, 按 3 维度严格分离):
  - L0 Sponsor (不变)
  - L1 PMO-Main (维度 1 业务项目整体采集)
  - L2 Plan-Agent (不变)
  - L2 Engineer-Agent (维度 2 研发 5 阶段采集)
  - L2 Monitor-Agent (新增, 维度 3 业务项目上报 + 上报合规监管)
  - L2 Reviewer-Agent (不变)
  - L2 Assessor-Agent (新增, 3 维度分别考核)
  - L2 Message-Broker-Agent (新增, 项目间消息经 PMO 中介)
- 3 维度架构 (业务项目整体 / 研发 5 阶段 / 业务项目上报)
- 业务项目 2 层合规契约 (业务项目整体 + 业务项目内研发 5 阶段)
- 3 层上报机制 (业务自采 + 业务上报 + PMO 存上报)
- 3 维度考核 (Assessor-Agent 按 3 维度分别考核)
- 项目间消息经 PMO 中介 (Message-Broker-Agent)
- 业务项目接入 PMO 5 步流程
- scripts/runtime/README.md (新建)

### Changed
- agent_base.py: 5 agent → 8 agent
- pmo_runtime.py: v0.2.0 → v0.2.1, 加 3 维度演示 + Assessor + Message-Broker

## [0.2.1] - 2026-06-18

### Added (DEC-2026-0002)

### Changed
- PMO 部署: 本地优先 (Q2)
- 不可变文档库: Git (Q4)
- 业务知识库: 接口契约, 不绑定实现 (Q3)

### Fixed
- (无)

### Removed
- (无)

## [0.1.0] - 2026-06-18

### Added
- 初始 PMO 平台搭建
- 0 章治理原则 (0.0.1 ~ 0.0.10)
- M0/M1/M2/M6/M7 任务清单 (24 任务)
- 1.1 PMO 自建项目启动
- 业务接入路径 (1 套)
- 不可变文档库 (Git)
- 决策日志 (schema + 1 决策样例)
- Memory 分级 (热/温/冷)
- 指标库 (业务/治理/工程三类)

### 关键决策
- DEC-2026-0001: PMO 1 套规范 + N 项目复用原则
