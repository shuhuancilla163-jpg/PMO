# Changelog (PMO 平台变更日志)

所有重要变更记录在这里 (含规范演进, 业务接入, 重大决策)。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### Added (DEC-2026-0002)
- 业务项目 2 层合规 (业务项目整体 + 业务项目内研发 5 阶段)
- 5 阶段研发角色 (Requirement-Engineer / Development-Engineer / Test-Engineer / Operations-Engineer / Evaluation-Engineer), PMO 监管, 业务项目可调
- 8 PMO 角色 (从 5 → 8, 按 3 维度严格分离): Sponsor / PMO-Main / Plan / Engineer / Monitor / Reviewer / Assessor / Message-Broker
- 3 维度架构 (业务项目整体 / 研发 5 阶段 / 业务项目内业务)
- 3 维度分别考核 (L2 PMO-Assessor-Agent)
- 3 维度监控 (L1 PMO-Main / L2 PMO-Engineer-Agent / L2 PMO-Monitor-Agent)
- 3 层上报机制 (业务项目自采 + 业务项目上报 + PMO 存上报)
- 项目间消息经 PMO 中介 (L2 PMO-Message-Broker-Agent)
- 业务项目接入 PMO 5 步流程
- 业务项目整体契约模板 + 业务项目研发 5 阶段契约模板
- 业务项目自管业务内容 (业务场景/业务 agent/业务流程/业务异常/业务指标)
- 业务项目上报关键指标 (5 项基础 + 自定义)
- PMO 监管上报合规 (3 项指标)
- 3 层异常拦截边界清晰化 (业务异常业务项目拦截, 研发异常 + 项目异常 PMO 实例拦截)
- 0.0.7 解耦原则严格化 (PMO 定规范, 业务项目管具体)

### Changed
- 业务 agent 不再固定 8 个, 业务项目按业务场景配置
- PMO 不提供业务场景模板, 业务项目自维护
- 业务项目模板结构 (新增 eng-roles/, messaging.yaml, reports/, 5 阶段产出目录)

### Fixed
- (无)

### Removed
- (无)

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
