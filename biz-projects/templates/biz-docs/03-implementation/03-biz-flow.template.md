# 03-biz-flow.template.md — 业务流编排模板

**templates/biz-docs/03-implementation/**

## 模板说明

此模板用于定义业务流编排和异常处理, 属于 m2.4 业务执行层骨架。

## 模板内容

```markdown
# 业务流编排 + 异常处理

**业务项目**: <project-id>
**版本**: v<major>.<minor>.<patch>
**阶段**: development
**创建时间**: <YYYY-MM-DD>

## 1. 业务流编排

### 1.1 业务 agent 交互顺序
<!-- 具体业务项目基于 Sponsor 需求定义 -->

### 1.2 输入输出
| 业务 agent | 输入 | 输出 |
|---|---|---|
| <!-- agent --> | <!-- 输入 --> | <!-- 输出 --> |

### 1.3 触发条件
<!-- 什么条件触发哪个业务 agent -->

## 2. 异常处理 (4 类)

| 异常类 | 定义 | 处理策略 | 回滚粒度 |
|---|---|---|---|
| 业务异常 (BizException) | 业务逻辑错误 | 业务 agent 自管 | 业务项目自定 |
| 数据异常 (DataException) | 数据完整性/一致性错误 | 业务 agent 自管 | 业务项目自定 |
| 集成异常 (IntegrationException) | 与外部系统交互错误 | 业务 agent 自管 | 业务项目自定 |
| 系统异常 (SystemException) | 系统级错误 | 业务 agent 自管 | 业务项目自定 |

### 2.1 回滚粒度
<!-- 具体业务项目定义回滚边界 -->

### 2.2 补偿策略
<!-- 具体业务项目定义补偿逻辑 -->
```

## 填充说明

AI Operator 基于 biz-design.md + Sponsor 需求填入具体内容。
