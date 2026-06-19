# 业务需求文档

**业务项目**: 1.1-pmo-self
**版本**: v1.0.0
**阶段**: requirement
**基于**: data-schema.yaml (E2) + glossary.yaml (E3)
**Git Commit**: 初始化需求文档 (biz.1.1-pmo-self.v1.0.0-rc.1)

## 1. 业务目标

PMO 自建系统, 实现 AI 驱动的 PMO 治理框架, 包括元规则治理、运行时执行、3 维度监控。

## 2. 核心业务实体 (基于 E2 data-schema)

| 实体 | 英文 | 中文 | 主要字段 |
|---|---|---|---|
| task | PMO 任务 | Task | task_id, title, phase, status, owner |
| decision | PMO 决策 | Decision | decision_id, title, status, approver |
| metric | PMO 指标 | Metric | metric_id, name, value, timestamp |

## 3. 业务术语 (基于 E3 glossary)

| 术语 | 定义 |
|---|---|
| meta-rule | PMO 元规则, 不可变治理规范 |
| phase | PMO 阶段 (M0/M1/M2/M6/M7) |
| compliance | 合规, 符合元规则要求 |
| self-evolution | 自进化, 数据驱动的持续优化 |

## 4. 非功能性需求 (NFR)

- **治理完整性**: 所有 PMO 行为有记录
- **可追溯性**: 所有决策可回溯到元规则
- **自进化**: 可基于数据持续优化

## 5. 业务 agent 职责 (基于 E3 roles)

| 业务 agent | 职责 |
|---|---|
| Sponsor | 发起任务/审批决策 |
| PMO-Main | 分配任务/协调 |
| Plan-Agent | 制定计划 |
| Engineer-Agent | 实施 |
| Monitor-Agent | 监控 |
| Assessor-Agent | 考核 |
| Reviewer-Agent | 审计 |
| Message-Broker-Agent | 消息路由 |
