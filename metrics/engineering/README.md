# 工程指标 (Engineering Metrics)

**工程实现层指标, 0.0.7 解耦, M7 选型时定具体指标**。

## 指标清单

| # | metric_id | 名称 | 单位 | 采集方式 | 频率 | 用途 |
|---|---|---|---|---|---|---|
| 1 | ENG-M-001 | **deploy_success_rate** (部署成功率) | % | 自动 | 每次部署 | 部署可靠性 |
| 2 | ENG-M-002 | **performance** (性能, 响应时间) | ms | 自动 | 每次请求 | 性能 SLA |
| 3 | ENG-M-003 | **availability** (可用性) | % | 自动 | 实时 | 系统可靠性 |
| 4 | ENG-M-004 | **exception_interception_rate** (异常拦截率) | % | 自动 | 每日 | 异常处理 |
| 5 | ENG-M-005 | **token_consumption** (Token 消耗) | token | 自动 | 每次请求 | Token 经济 |
| 6 | ENG-M-006 | **memory_usage** (Memory 使用) | MB | 自动 | 实时 | Memory 配额 |
| 7 | ENG-M-007 | **storage_usage** (存储使用) | MB | 自动 | 实时 | 存储配额 |
| 8 | ENG-M-008 | **concurrency** (并发数) | 个 | 自动 | 实时 | 并发配额 |
| 9 | ENG-M-009 | **disaster_recovery_time** (灾备恢复时间) | 秒 | 自动 | 灾备演练 | 灾备能力 |
| 10 | ENG-M-010 | **mcp_call_success_rate** (MCP 调用成功率) | % | 自动 | 每日 | MCP 契约 |

## 0.0.7 解耦

- 工程指标**不绑定**具体工程实现
- 具体采集工具由工程实现层选 (M7)
- 指标 schema 是治理层, 采集方式是工程层

## 告警规则

| 指标 | 阈值 | 严重性 | 通知 |
|---|---|---|---|
| deploy_success_rate < 95% | warning | pmo-instance |
| performance > 5000ms | warning | pmo-instance |
| availability < 99% | critical | pmo-instance + sponsor |
| mcp_call_success_rate < 95% | warning | pmo-instance |
| disaster_recovery_time > 60s | critical | pmo-instance + sponsor |
