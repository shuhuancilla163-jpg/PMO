# 业务项目模板 (biz-projects/templates)

**每个业务项目按 1 套模板创建** (0.0.10 1 套规范)。

## 模板结构

```
biz-projects/<biz-project-id>/
├── README.md              # 项目说明 (目标, 任务, 接入路径)
├── register.yaml          # 业务注册 (PMO 实例解析)
├── checklist.md           # 启动 checklist (基础 6 项 + Sponsor/复盘/规则)
├── state/                 # 业务状态 (项目内)
│   ├── current.json       # 当前状态
│   └── history/           # 状态历史
├── tasks/                 # 业务任务
│   ├── queue/             # 业务任务队列
│   └── done/              # 已完成任务
├── metrics/               # 业务指标 (项目内, 基础 5 + 自定义)
├── reports/               # 业务报告
│   ├── daily/             # 日常报告
│   └── phase/             # 阶段报告
├── knowledge/             # 业务专有知识 (本项目)
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

## 接入步骤

1. 复制模板到 `biz-projects/<biz-project-id>/`
2. 修改 `register.yaml` (填业务项目信息)
3. 修改 `checklist.md` (勾选已就绪项)
4. 提交到 Git (业务项目注册)
5. 通知 PMO 实例 (m2.6 业务注册流程)
6. 业务项目状态 = active, 接入 PMO

## 关键

- **1 套模板, N 项目复用** (0.0.10)
- **业务项目自管** (项目目录, 状态, 任务, 知识, 归档)
- **PMO 实例监管** (注册, 配额, 隔离, 异常拦截)
- **Sponsor 监督** (重大决策, 指标看板, MVP 验收)
