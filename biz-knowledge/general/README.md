# 业务通用知识库 (biz-knowledge/general)

**所有业务项目共享**, 业务项目可读, 但不能改 (Q27 通用层)。

## 用途

- 通用术语 (PMO 通用术语)
- 通用规范 (PMO 通用规范引用)
- 通用 SOP 模板 (业务 SOP 模板骨架)
- 通用契约模板 (PMO↔业务契约模板)

## 写入规则

- **只读**: 业务项目**不能修改**通用知识库
- **PMO 实例可追加**: 新通用知识由 PMO 实例评审后追加
- **版本管理**: Git 跟踪, 变更走决策流程

## 目录结构

```
biz-knowledge/general/
├── README.md (本文件)
├── terms/                 # 通用术语
│   ├── pmo-terms.md
│   ├── governance-terms.md
│   └── biz-terms.md
├── specs/                 # 通用规范引用
│   ├── governance-refs.md
│   ├── engineering-refs.md
│   └── value-refs.md
├── sop-templates/         # 通用 SOP 模板
│   ├── analysis-sop.md
│   ├── decision-sop.md
│   └── review-sop.md
└── contract-templates/    # 通用契约模板
    ├── biz-contract-template.md
    └── interface-template.md
```

## 与业务专有知识库区别

| 维度 | 通用 (本目录) | 专有 (biz-knowledge/specific/) |
|---|---|---|
| 访问 | 所有业务项目可读 | 仅本项目可访问 |
| 修改 | PMO 实例评审后追加 | 业务项目自定 |
| 用途 | 通用术语/规范/模板 | 业务专有术语/schema/SOP |
