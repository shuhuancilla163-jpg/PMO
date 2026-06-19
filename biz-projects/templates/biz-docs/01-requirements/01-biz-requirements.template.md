# 01-biz-requirements.template.md — 业务需求文档模板

**templates/biz-docs/01-requirements/**

## 模板说明

此模板用于业务需求阶段 (Requirement 阶段), 基于 E2 (data-schema.yaml) 和 E3 (glossary.yaml) 产出业务需求文档。

## 模板内容

```markdown
# 业务需求文档

**业务项目**: <project-id>
**版本**: v<major>.<minor>.<patch>
**阶段**: requirement
**基于**: data-schema.yaml (E2) + glossary.yaml (E3)
**创建时间**: <YYYY-MM-DD>

## 1. 业务目标

### 1.1 核心目标
<!-- 具体业务项目填入 -->

### 1.2 成功标准
<!-- 具体业务项目填入 -->

## 2. 业务实体 (基于 E2 data-schema)

### 2.1 核心实体
<!-- 基于 data-schema.yaml entities 填入 -->

### 2.2 实体关系
<!-- ER 图或文字描述 -->

## 3. 业务术语 (基于 E3 glossary)

### 3.1 术语表
<!-- 基于 glossary.yaml terms 填入 -->

### 3.2 业务 agent 角色
<!-- 基于 glossary.yaml roles 填入 (DEC-2026-0003 边界: 不与 5 阶段研发 role 重名) -->

## 4. 非功能性需求 (NFR)

| 类型 | 要求 |
|---|---|
| 性能 | <!-- 具体业务项目填入 --> |
| 安全 | <!-- 具体业务项目填入 --> |
| 可用性 | <!-- 具体业务项目填入 --> |

## 5. 约束条件

<!-- 具体业务项目填入 -->

## 6. 验收标准

| 场景 | 预期结果 |
|---|---|
| <!-- 场景 --> | <!-- 预期 --> |

## 7. 风险登记

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| <!-- 风险 --> | <!-- 影响 --> | <!-- 缓解 --> |
```

## 填充说明

AI Operator 基于 Sponsor 业务需求 + E2 + E3 填入具体内容。
