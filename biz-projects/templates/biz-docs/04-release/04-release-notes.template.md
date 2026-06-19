# 04-release-notes.template.md — 发布说明模板

**templates/biz-docs/04-release/**

## 模板说明

此模板用于发布阶段 (Release 阶段), 基于 biz-version-store 的 semver 版本管理产出发布说明。

## 模板内容

```markdown
# 发布说明

**业务项目**: <project-id>
**版本**: v<major>.<minor>.<patch>
**Git tag**: biz.<project-id>.v<major>.<minor>.<patch>
**发布日期**: <YYYY-MM-DD>

## 1. 版本概述

<!-- 本版本主要变化 -->

## 2. 变更清单

### 2.1 新增
<!-- 本版本新增内容 -->

### 2.2 变更
<!-- 本版本变更内容 -->

### 2.3 修复
<!-- 本版本修复内容 -->

## 3. PMO 元数据

| 元数据 | 值 |
|---|---|
| E1 (业务项目) | register.yaml |
| E2 (数据模型) | data-schema.yaml |
| E3 (术语表) | glossary.yaml |

## 4. 升级注意事项

<!-- 具体业务项目填入 -->
```

## 填充说明

AI Operator 基于 Git tag + biz-version-store 填入版本信息。
