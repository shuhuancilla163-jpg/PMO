# 业务不可变文档 (m2.2, F1)

**框架态: 具体内容待具体业务项目填入**

---

## 01-requirements/ — 需求阶段

### biz-requirements.md (框架态)

```markdown
# 业务需求文档

**业务项目**: <project-id> (框架态, 具体业务项目填入)
**版本**: v0.1.0
**阶段**: requirement
**基于**: data-schema.yaml (E2) + glossary.yaml (E3)

## 1. 业务需求

### 1.1 核心业务实体 (基于 E2 data-schema)
<!-- 具体业务项目填入 -->

### 1.2 业务术语 (基于 E3 glossary)
<!-- 具体业务项目填入 -->

### 1.3 非功能性需求 (NFR)
<!-- 具体业务项目填入 -->
```

---

## 02-design/ — 设计阶段

### biz-design.md (框架态)

```markdown
# 业务设计文档

**业务项目**: <project-id>
**版本**: v0.1.0
**阶段**: development

## 1. 业务流
<!-- 具体业务项目填入 -->

## 2. 数据模型
<!-- 基于 E2 data-schema -->
```

### api-contract.md (框架态, m2.5 前身)

```markdown
# API 契约

**业务项目**: <project-id>
**版本**: v0.1.0
```

---

## 03-implementation/ — 实施阶段

### biz-flow.md (框架态, m2.4 前身)

```markdown
# 业务流编排

**业务项目**: <project-id>
**版本**: v0.1.0
```

### exception-handling.md (框架态, m2.4 前身)

```markdown
# 业务异常定义

**业务项目**: <project-id>
**版本**: v0.1.0
```

---

## 04-release/ — 发布阶段

### release-notes.md (框架态)

```markdown
# 发布说明

**业务项目**: <project-id>
**版本**: v0.1.0
**Git tag**: biz.<project-id>.v0.1.0
```

### deployment.md (框架态)

```markdown
# 部署文档

**业务项目**: <project-id>
**版本**: v0.1.0
```
