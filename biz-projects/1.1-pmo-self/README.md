# 1.1 PMO 系统自建

**业务项目 ID**: 1.1
**项目类型**: PMO 平台搭建 (当前阶段, 第一阶段)
**Sponsor**: 1 个 (你)
**状态**: active

## 项目目标

1. 完成 PMO 平台搭建 (M0 + M1 + M2 + M6 + M7)
2. 建立 1 套 PMO 治理规范 (0.0.1 ~ 0.0.10)
3. 部署 1 个 PMO 实例 (本地)
4. 端到端自测 (M6.1 + M6.2)
5. 工程实现层选型 (M7)

## 任务清单

| 阶段 | 任务 | 复杂度 | 状态 |
|---|---|---|---|
| M0 | m0.1 存储层 | 4 | in_progress |
| M0 | m0.2 运行时 | 5 | pending |
| M0 | m0.3 部署 | 3 | pending |
| M0 | m0.4 运维 | 4 | pending |
| M0 | m0.5 自测 | 2 | pending |
| M1 | m1.1 元规则 | 3 | pending |
| M1 | m1.2 合规 | 4 | pending |
| M1 | m1.3 核心执行 | 5 | pending |
| M1 | m1.4 agents | 5 | pending |
| M1 | m1.5 自检 | 4 | pending |
| M2 | m2.1 元数据 | 2 | pending |
| M2 | m2.2 不可变 | 2 | pending |
| M2 | m2.3 8 业务 agent 骨架 | 3 | pending |
| M2 | m2.4 执行层骨架 | 2 | pending |
| M2 | m2.5 跨边界契约 | 3 | pending |
| M2 | m2.6 业务项目管理 | 5 | pending |
| M6 | m6.1 端到端自测 | 5 | pending |
| M6 | m6.2 自测报告 | 3 | pending |
| M7 | m7.1 评估 agent 框架 | 2 | pending |
| M7 | m7.2 评估工具层 | 2 | pending |
| M7 | m7.3 评估部署 | 2 | pending |
| M7 | m7.4 评估模型 | 2 | pending |
| M7 | m7.5 评估存储 | 2 | pending |
| M7 | m7.6 推荐报告 | 4 | pending |

**总任务数**: 24
**总复杂度**: 78

## 业务接入路径 (复用 0.0.10 1 套)

- 业务注册: `biz-projects/1.1-pmo-self/register.yaml`
- 业务状态: `tasks/state/1.1-pmo-self.json`
- 业务配额: `config/biz-quota/1.1-pmo-self.yaml`
- 业务归档: `archive/biz-projects/1.1-pmo-self/`
- 业务监控: `metrics/business/1.1-pmo-self/`
- 业务 checklist: `biz-projects/1.1-pmo-self/checklist.md`
- 业务契约: `immutable/2-biz-specs/contract-1.1-pmo-self.md`

## 业务优先级

1.1 启动: PMO 平台搭建 + 自测 + 选型 (优先级: P0, 最高)
1.2 启动: 业务系统 (1.1 完成后, 优先级: P1)
1.3/1.4 启动: 后续业务 (优先级: 后期定)
