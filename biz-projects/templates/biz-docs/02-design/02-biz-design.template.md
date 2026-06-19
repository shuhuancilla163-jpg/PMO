# 02-biz-design.template.md — 业务设计文档模板

**templates/biz-docs/02-design/**

## 模板说明

此模板用于设计阶段 (Development 阶段), 基于 biz-requirements.md 产出业务设计文档。

## 模板内容

```markdown
# 业务设计文档

**业务项目**: <project-id>
**版本**: v<major>.<minor>.<patch>
**阶段**: development
**基于**: biz-requirements.md
**创建时间**: <YYYY-MM-DD>

## 1. 业务流架构

### 1.1 业务流图
<!-- 文字描述业务流, 或 Mermaid 图 -->

### 1.2 业务 agent 交互
<!-- 基于 E3 glossary roles 列出 agent 及其职责 -->

## 2. 数据模型

### 2.1 实体定义
<!-- 基于 data-schema.yaml entities -->

### 2.2 数据流
<!-- 数据如何流转 -->

## 3. 接口设计

### 3.1 内部接口 (业务 agent ↔ 业务 agent)
<!-- 业务 agent 之间的接口, 业务项目自定 -->

### 3.2 外部接口 (业务 ↔ PMO)
<!-- PMO 监管接口 (消息/上报), 业务项目自定 -->

## 4. 安全设计

<!-- 具体业务项目填入 -->

## 5. 异常设计

<!-- 4 类异常定义, 参考 exception-handling.md 模板 -->
```

## 填充说明

AI Operator 基于 biz-requirements.md + E2 + E3 填入具体内容。
