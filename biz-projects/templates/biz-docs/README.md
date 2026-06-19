# biz-docs/ 业务不可变文档模板 (m2.2, F1)

业务项目的业务产出文档模板, 业务项目复制到 `biz-projects/<id>/biz-docs/` 后填写。

## 目录结构

```
biz-docs/
├── 01-requirements/           # 需求阶段产出
│   ├── README.md             # 需求阶段概览
│   ├── biz-requirements.md  # 业务需求 (必填, 基于 E2/E3)
│   └── nfr.md              # 非功能性需求 (选填)
├── 02-design/               # 设计阶段产出
│   ├── README.md
│   ├── biz-design.md       # 业务设计 (必填)
│   └── api-contract.md     # API 契约 (选填, m2.5 前身)
├── 03-implementation/       # 实施阶段产出
│   ├── README.md
│   ├── biz-flow.md         # 业务流编排 (必填, m2.4 前身)
│   └── exception-handling.md # 业务异常定义 (选填, m2.4 前身)
└── 04-release/              # 发布阶段产出
    ├── README.md
    ├── release-notes.md    # 发布说明 (必填, semver)
    └── deployment.md       # 部署文档 (选填)
```

## 使用方式

1. 业务项目在 m2.1 接入后 (已有 E1/E2/E3)
2. 复制本目录到 `biz-projects/<id>/biz-docs/`
3. 按阶段填写文档
4. Git commit 每阶段文档
5. 发布时 Git tag: `biz.<id>.v<MAJOR>.<MINOR>.<PATCH>`

## 不可变规则

- 发布后的文档不可修改
- 变更通过新文档追加
- Git 历史保证不可变
