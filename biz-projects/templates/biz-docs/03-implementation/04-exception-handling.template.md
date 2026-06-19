# 04-exception-handling.template.md — 业务异常处理模板

**templates/biz-docs/03-implementation/**

## 模板说明

此模板用于定义 4 类业务异常, 属于 m2.4 业务执行层骨架。
具体异常内容由业务项目基于 Sponsor 需求填入。

## 模板内容

```markdown
# 业务异常处理

**业务项目**: <project-id>
**版本**: v<major>.<minor>.<patch>
**阶段**: development
**创建时间**: <YYYY-MM-DD>

## 1. 4 类异常定义

| 异常类 | 父类 | 触发条件 | 严重级别 |
|---|---|---|---|
| BizException | Exception | 业务逻辑错误 | error |
| DataException | Exception | 数据完整性/一致性错误 | error |
| IntegrationException | Exception | 外部系统交互错误 | warning |
| SystemException | Exception | 系统级错误 | critical |

### 1.1 BizException — 业务异常
<!-- 具体业务项目填入业务异常类型 -->

### 1.2 DataException — 数据异常
<!-- 具体业务项目填入数据异常类型 -->

### 1.3 IntegrationException — 集成异常
<!-- 具体业务项目填入集成异常类型 -->

### 1.4 SystemException — 系统异常
<!-- 具体业务项目填入系统异常类型 -->

## 2. 回滚粒度

> 业务回滚粒度由业务项目内部约定, PMO 不规定。

<!-- 具体业务项目定义回滚边界 -->
<!-- 例如: 单事务回滚 / 补偿事务 / 全量回滚 -->

## 3. 补偿策略

> 补偿策略由业务项目内部约定, PMO 不规定。

<!-- 具体业务项目定义补偿逻辑 -->
<!-- 例如: 补偿事务 / 重试 / 人工介入 -->
```

## 填充说明

AI Operator 基于 Sponsor 需求填入具体异常类型和处理策略。
