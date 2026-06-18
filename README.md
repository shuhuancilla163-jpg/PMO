# PMO 平台 (Project Management Office)

**1 套 PMO 治理规范, 1 个 PMO 实例, N 个业务项目复用, 1 个 Sponsor 介入** (0.0.10)

## 目录结构

```
PMO/
├── immutable/             # 不可变文档库 (Git 不可变, 只追加, 不修改)
│   ├── 0-governance/      # 治理原则 (0.0.1 ~ 0.0.10)
│   ├── 1-pmo-specs/       # PMO 规范 (M0/M1/M2/M6/M7 规范)
│   ├── 2-biz-specs/       # 业务规范 (业务项目接入契约)
│   └── 3-decisions/       # 不可变决策文档
├── decisions/             # 决策日志 (append-only)
│   ├── active/            # 当前生效的决策
│   ├── archive/           # 历史决策
│   └── schema.json        # 决策日志 schema
├── memory/                # Memory 分级
│   ├── hot/               # 热 Memory (当前活跃, .gitignore)
│   ├── warm/              # 温 Memory (近期, Git 跟踪)
│   └── cold/              # 冷 Memory (历史, Git 跟踪)
├── config/                # 配置
│   ├── pmo.config.yaml    # PMO 主配置
│   ├── agents.yaml        # agent 配置
│   └── policies.yaml      # 策略配置
├── versions/              # 版本管理 (Git tag/release + semver)
│   ├── v0.1.0/
│   ├── v0.2.0/
│   └── CHANGELOG.md
├── tasks/                 # 任务队列
│   ├── queue/             # 队列 (active/, processing/, done/)
│   ├── state/             # 状态机
│   └── schema.json        # 任务 schema
├── biz-knowledge/         # 业务知识库 (2 层)
│   ├── general/           # 通用知识 (所有项目共享)
│   └── specific/          # 业务专有 (项目隔离)
├── metrics/               # 指标库
│   ├── business/          # 业务指标 (基础 5 项)
│   ├── governance/        # 治理指标
│   ├── engineering/       # 工程指标
│   └── schema.json        # 指标 schema
├── biz-projects/          # 业务项目
│   ├── 1.1-pmo-self/      # 1.1 PMO 自建 (当前)
│   ├── 1.2-biz/           # 1.2 业务 (未来)
│   └── templates/         # 业务项目模板
├── prompts/               # agent prompts
├── hooks/                 # Cursor hooks (按需)
├── scripts/               # 运行时脚本
├── docs/                  # 文档
├── tests/                 # 测试
├── reports/               # 报告
└── archive/               # 归档
```

## 核心原则 (摘要)

| 原则 | 含义 |
|---|---|
| 0.0.7 解耦 | 价值/治理/工程/项目实现 4 层解耦 |
| 0.0.8 自进化 | PMO 规范自进化, 不绑定模型自进化 |
| 0.0.9 基座完善 | 第一阶段无业务, 完善 PMO 基座 |
| 0.0.10 1 规范 N 项目 | 1 套 PMO 规范, 1 个 PMO 实例, N 个业务项目 |
| 0.0.10 三权分立 | L0 Sponsor 监督, L1 PMO 行政, L2 司法制衡 |
| 0.0.10 3 层异常拦截 | PMO 规范不参与业务, PMO 实例拦截项目级, 业务项目拦截自身 |
| 0.0.10 3 层告警 | 业务自给, 重大→PMO, PMO→Sponsor |
| 0.0.10 指标可贯彻 | 业务/治理/工程三类指标, 不只报告 |

## 业务接入 (1 套契约)

- 业务注册 → `biz-projects/<project-id>/`
- 业务状态 → `tasks/state/<project-id>.json`
- 业务配额 → `config/biz-quota/<project-id>.yaml`
- 业务归档 → `archive/biz-projects/<project-id>/`
- 业务监控 → `metrics/business/<project-id>/`
- 业务 checklist → `biz-projects/<project-id>/checklist.md`
- 业务契约 → `immutable/2-biz-specs/contract-<project-id>.md`

## Sponsor 介入节点

- 1.1 启动 (M0 启动)
- 1.2 启动 (M6 自测通过后)
- 1.3/1.4 启动 (1.2 完成后)
- 重大决策 (变更治理规则, 重大异常, 发布)
- MVP 验收 (业务流跑通后)
- 阶段验收 (每 M 阶段完成时)
