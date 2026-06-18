# 业务指标 (Business Metrics) — 基础 5 项 (Q13)

**业务项目核心指标, 5 项基础** (业务项目可加自定义)。

## 基础 5 项

| # | metric_id | 名称 | 单位 | 采集方式 | 频率 | 用途 |
|---|---|---|---|---|---|---|
| 1 | BIZ-M-001 | **flow_latency** (业务流耗时) | 秒 | 自动 (运行时统计) | 每次业务流 | 业务流性能, 业务 SLA |
| 2 | BIZ-M-002 | **exception_rate** (业务异常率) | % | 自动 (异常/总) | 每小时 | 业务稳定性 |
| 3 | BIZ-M-003 | **pass_rate** (业务通过率) | % | 自动 (通过/总) | 每小时 | 业务质量 |
| 4 | BIZ-M-004 | **rollback_rate** (业务回滚率) | % | 自动 (回滚/总) | 每小时 | 业务可靠性 |
| 5 | BIZ-M-005 | **token_consumption** (Token 消耗) | token | 自动 (Token 计数) | 每次业务流 | 业务成本, 配额 |

## 业务项目自定义

业务项目可加自定义指标, 写入 `metrics/business/<biz-project-id>/`, 需符合 schema.json。

## 指标可贯彻 (Sponsor 点出)

- 指标**必须跑出来** (自动采集, 不靠手填)
- 指标**必须可审计** (m1.2 指标审计)
- 指标**必须 Sponsor 可看** (指标看板, 不只 PMO 报告)

## 跨项目隔离

- 业务指标按业务项目隔离 (Q24 全隔离)
- PMO 实例管所有业务项目指标
- 业务项目只能看自己的指标 (除非 Sponsor 授权)

## 告警规则 (默认)

| 指标 | 阈值 | 严重性 | 通知 |
|---|---|---|---|
| flow_latency > 300s | critical | biz-project |
| exception_rate > 5% | warning | biz-project |
| exception_rate > 20% | critical | biz-project + pmo-instance |
| pass_rate < 80% | warning | biz-project |
| pass_rate < 50% | critical | biz-project + pmo-instance |
| rollback_rate > 10% | critical | biz-project + pmo-instance + sponsor |
| token_consumption > 配额 80% | warning | biz-project |
| token_consumption > 配额 100% | critical | biz-project + pmo-instance |
