# 0-治理 (0-governance) 元规则库

**PMO 治理层不可变文档库** (Git 不可变, 修改需 Sponsor 授权 + DEC-2026-0002)

## 12 项元规则 (DEC-2026-0002 后 8 → 12)

| # | 文件 | 标题 | 关键 |
|---|---|---|---|
| 0.0.1 | [0.0.1-five-values.md](./0.0.1-five-values.md) | 五大核心价值 (Sponsor 视角) | 高效流程/规范/可控/验收/优化 |
| 0.0.2 | [0.0.2-engineering.md](./0.0.2-engineering.md) | 工程化 (技术实现) | Token/上下文/Memory 分级 |
| **0.0.3** | [0.0.3-value-task-mapping.md](./0.0.3-value-task-mapping.md) | **价值→任务映射** | 每个任务必须有价值归属 |
| **0.0.4** | [0.0.4-value-failure-detection.md](./0.0.4-value-failure-detection.md) | **价值→失败检测** | 价值失效检测 + 4 步修复流程 |
| 0.0.5 | [0.0.5-task-mgmt.md](./0.0.5-task-mgmt.md) | 任务管理原则 (Sponsor 定的) | 不算人天, 关注任务完成度 |
| 0.0.6 | [0.0.6-biz-flow.md](./0.0.6-biz-flow.md) | 业务流程 (Sponsor 介入节点) | 7 个 Sponsor 介入节点 |
| 0.0.7 | [0.0.7-decoupling-4layers.md](./0.0.7-decoupling-4layers.md) | 价值-治理-工程-项目实现 解耦 | 治理不绑工程, 工程不绑项目 |
| 0.0.8 | [0.0.8-self-evolution.md](./0.0.8-self-evolution.md) | 自进化机制 | 反思 + 规则 A/B + 灰度 + 熔断 |
| 0.0.9 | [0.0.9-base-completion.md](./0.0.9-base-completion.md) | 基座完善 (第一阶段核心) | M0/M1/M2 完整基座 |
| 0.0.10 | [0.0.10-1spec-Nprojects.md](./0.0.10-1spec-Nprojects.md) | PMO 1 套规范 + N 项目复用 | 1 PMO 实例管 N 业务项目 |
| **0.0.11** | [0.0.11-biz-project-2layer-compliance.md](./0.0.11-biz-project-2layer-compliance.md) | **业务项目 2 层合规 (DEC-2026-0002)** | 业务项目整体 + 业务项目内研发 5 阶段 |
| **0.0.12** | [0.0.12-3dimension-architecture.md](./0.0.12-3dimension-architecture.md) | **3 维度架构 (DEC-2026-0002)** | 业务项目整体 / 研发 5 阶段 / 业务项目内业务 |

## 不可变性 (Immutable)

**0-governance 目录下所有文档都是不可变**:
- 修改需 Sponsor 授权
- 修改需 DEC-2026-XXXX 决策日志
- 修改需 Git tag + 不可变文档库归档

## DEC-2026-0002 调整 (2026-06-18)

Sponsor 平等讨论后, 增加 4 项元规则:
- 0.0.3 价值→任务映射 (之前没有单独文件)
- 0.0.4 价值→失败检测 (之前没有单独文件)
- 0.0.11 业务项目 2 层合规 (新增)
- 0.0.12 3 维度架构 (新增)

**调整原因**: Sponsor 推动业务项目分业务组 + 研发组 + 3 维度考核 + 业务项目自管业务内容, 这些新原则需要 4 项新元规则固化。

## 关键决策

- **DEC-2026-0001**: 0.0.10 PMO 1 套规范 + N 项目复用原则
- **DEC-2026-0002**: 14 块关键调整 (2026-06-18, 加 0.0.3/0.0.4/0.0.11/0.0.12)
