# 业务项目 1.x-biz-template (通用业务项目骨架模板)

**通用业务项目骨架, 具体业务 domain 由 Sponsor 后续注入**

## 框架态原则

> PMO 框架不管具体业务 domain。具体业务 (如量化金融/电商/医疗) 由 Sponsor 后续定义。
> `1.x-biz-template` 只提供业务项目接入 PMO 所需的**空骨架**, 不预置任何业务假设。

## 项目概述

- **业务项目 ID**: `1.x-biz-template`
- **性质**: 通用业务项目骨架模板
- **状态**: template (不可直接使用, 需复制后填入具体业务内容)
- **用途**: AI Operator 基于此模板 + Sponsor 业务需求 → 创建具体业务项目

## 业务项目结构

```
1.x-biz-template/
├── README.md              # 本文件
├── register.yaml          # 业务项目注册 (E1, 空模板)
├── data-schema.yaml      # 业务数据模型 (E2, 空模板)
├── glossary.yaml          # 业务术语表 (E3, 空模板)
├── eng-roles/            # 5 阶段研发 agent (PMO 监管, 0.0.13)
│   ├── 01-requirement-engineer.py
│   ├── 02-development-engineer.py
│   ├── 03-test-engineer.py
│   ├── 04-operations-engineer.py
│   ├── 05-evaluation-engineer.py
│   ├── register.yaml
│   └── README.md
├── biz-agents/           # 业务 agent 框架 (空目录)
│   └── README.md         # 框架说明: 业务 agent 由具体业务项目自定
├── biz-docs/             # 业务不可变文档 (空骨架)
│   ├── 01-requirements/
│   ├── 02-design/
│   ├── 03-implementation/
│   └── 04-release/
├── reports/              # 5 阶段上报 (PMO 采集源)
└── biz-data/            # 业务数据 (业务自存, PMO 不存)
```

## 业务项目 2 类 agent (框架说明)

### 1. eng-roles/ — 5 阶段研发 agent (PMO 监管)

- 物理位置: `eng-roles/`
- 数量: 5 个 (每个阶段一个)
- 实施: 业务项目从 `PMO/templates/eng-roles/` 复制 + 调整
- PMO 监督: 7 项合规 (0.0.13)
- 元规则: 0.0.13

### 2. biz-agents/ — 业务 agent (业务自管)

- 物理位置: `biz-agents/`
- 数量: **具体业务项目自定**
- 实施: **具体业务项目完全自定**
- PMO 监督: **不监督内容**
- 元规则: 0.0.14

> **注意**: biz-agents/ 是空目录, 具体业务 agent 在业务项目创建时由 Sponsor 需求驱动定义。

## 如何使用 (AI Operator 操作手册)

```
1. Sponsor 给出具体业务需求
   例如: "我要做一个电商系统" 或 "我要做一个医疗系统"

2. AI Operator 基于 1.x-biz-template 创建具体业务项目
   cp -r 1.x-biz-template biz-projects/1.3-my-project

3. AI Operator 填入具体内容:
   - register.yaml: 填入业务名称/类型/版本
   - data-schema.yaml: 定义业务实体
   - glossary.yaml: 定义业务术语
   - biz-agents/: 定义具体业务 agent
   - biz-docs/: 产出业务文档

4. AI Operator 向 Sponsor 汇报, Sponsor 审批
```

## PMO 监管 vs 业务自管

| 层级 | PMO 监管 | 业务自管 |
|---|---|---|
| 5 阶段研发 agent (eng-roles/) | ✅ 监管 (0.0.13) | - |
| 业务 agent (biz-agents/) | ❌ 不监管 | ✅ 业务自管 |
| 业务数据 (biz-data/) | ❌ 不存 | ✅ 业务自存 |
| 业务不可变文档 (biz-docs/) | ✅ 验证完整性 | ✅ 业务自写 |

## 关键原则 (框架态)

- **PMO 只管治理骨架, 不管具体业务 domain**
- **具体业务 domain 由 Sponsor 后续注入**
- **业务 agent 数量/名字/责任由具体业务项目自定**
- **历史参考示例在 `1.x-examples/quant-finance/`**
