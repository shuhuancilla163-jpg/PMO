# 业务项目模板 (biz-projects/templates)

**每个业务项目按 1 套模板创建** (0.0.10 1 套规范)。

## 模板结构 (DEC-2026-0002 调整后)

```
biz-projects/<biz-project-id>/
├── README.md              # 项目说明 (目标, 任务, 接入路径)
├── register.yaml          # 业务注册 (PMO 实例解析)
├── checklist.md           # 启动 checklist (基础 6 项 + Sponsor/复盘/规则)
├── messaging.yaml         # 业务项目消息订阅/发布主题 (新, DEC-2026-0002)
├── reports/               # 业务项目上报 (新, DEC-2026-0002)
│   ├── metrics.yaml       # 上报关键指标
│   ├── exceptions.yaml    # 上报业务异常
│   └── resources.yaml     # 上报资源使用
├── state/                 # 业务状态 (项目内)
│   ├── current.json       # 当前状态
│   └── history/           # 状态历史
├── eng-roles/             # 业务项目研发 5 阶段 (新, DEC-2026-0002)
│   ├── requirement.yaml   # 需求阶段角色
│   ├── development.yaml   # 研发阶段角色
│   ├── test.yaml          # 测试阶段角色
│   ├── operations.yaml    # 运维阶段角色
│   └── evaluation.yaml    # 评估阶段角色
├── requirement/           # 需求阶段产出 (新, DEC-2026-0002)
├── development/           # 研发阶段产出 (新, DEC-2026-0002)
├── test/                  # 测试阶段产出 (新, DEC-2026-0002)
├── operations/            # 运维阶段产出 (新, DEC-2026-0002)
├── evaluation/            # 评估阶段产出 (新, DEC-2026-0002)
├── tasks/                 # 业务任务
│   ├── queue/             # 业务任务队列
│   └── done/              # 已完成任务
├── metrics/               # 业务指标 (项目内, 基础 5 + 自定义)
├── knowledge/             # 业务专有知识 (本项目, 业务自管)
│   ├── terms.md
│   ├── data-schema.md
│   ├── sop/
│   └── best-practices/
└── archive/               # 业务归档 (项目结束后)
    ├── data/
    ├── documents/
    ├── project/
    └── resource/
```

## 业务项目接入 5 步流程 (DEC-2026-0002)

1. **业务项目注册** (m2.6 业务注册) — 填 `register.yaml` + 签 2 份契约
2. **业务项目内研发 5 阶段声明** (m2.3 + m2.6) — 在 `eng-roles/` 声明
3. **业务项目内业务配置** (业务项目自管) — 业务场景/业务 agent/业务流程/业务异常/业务指标
4. **业务项目接入 PMO 消息机制** (m2.5 跨边界契约) — `messaging.yaml`
5. **业务项目接入 PMO 监管** (m1.3 + m0.4) — `reports/` 上报关键指标

详细见: [业务项目接入 PMO 5 步流程](../docs/biz-project-onboarding-5-steps.md)

## 契约模板 (DEC-2026-0002)

- [业务项目整体契约模板](./contract-project-overall.md) — 业务项目 ID/名称/类型 + m2.6 7 项
- [业务项目研发 5 阶段契约模板](./contract-eng-5-stages.md) — 5 阶段角色 + PMO 7 项

## 接入步骤

1. 复制模板到 `biz-projects/<biz-project-id>/`
2. 修改 `register.yaml` (填业务项目信息)
3. 签 2 份契约 (业务项目整体 + 研发 5 阶段)
4. 在 `eng-roles/` 声明用了哪些研发角色
5. 业务项目自管业务 (业务场景/业务 agent/业务流程/业务异常/业务指标)
6. 在 `messaging.yaml` 声明消息订阅/发布主题
7. 在 `reports/` 配置上报关键指标
8. 修改 `checklist.md` (勾选已就绪项)
9. 提交到 Git (业务项目注册)
10. 通知 PMO 实例 (m2.6 业务注册流程)
11. 业务项目状态 = active, 接入 PMO

## 关键 (DEC-2026-0002)

- **1 套模板, N 项目复用** (0.0.10)
- **业务项目自管** (业务 agent/业务流程/业务异常/业务指标)
- **PMO 实例监管** (注册/配额/隔离/异常拦截/上报合规)
- **Sponsor 监督** (重大决策, 指标看板, MVP 验收)
- **3 维度架构** (业务项目整体 / 研发 5 阶段 / 业务项目内业务)
- **5 阶段研发角色** (PMO 监管, 业务项目可调)
- **3 层上报机制** (业务自采 + 业务上报 + PMO 存上报)
- **3 维度分别考核** (PMO-Assessor-Agent)
- **项目间消息经 PMO 中介** (PMO-Message-Broker-Agent)
