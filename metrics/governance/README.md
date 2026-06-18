# 治理指标 (Governance Metrics)

**PMO 治理层指标, 防止 PMO 自治粉饰** (Sponsor 点出)。

## 指标清单

| # | metric_id | 名称 | 单位 | 采集方式 | 频率 | 用途 |
|---|---|---|---|---|---|---|
| 1 | GOV-M-001 | **phase_gate_pass_rate** (阶段门控通过率) | % | 自动 | 阶段完成时 | 治理质量 |
| 2 | GOV-M-002 | **decision_log_completeness** (决策日志完整度) | % | 自动 (有日志/总决策) | 每日 | 治理可审计 |
| 3 | GOV-M-003 | **self_check_coverage** (自检覆盖率) | % | 自动 (已自检/总任务) | 每任务 | 治理自检 |
| 4 | GOV-M-004 | **self_evolution_count** (自进化次数) | 次 | 自动 | 每月 | 治理演进 |
| 5 | GOV-M-005 | **biz_project_count** (业务项目数) | 个 | 自动 | 实时 | 治理覆盖 |
| 6 | GOV-M-006 | **exception_interception_rate** (异常拦截率) | % | 自动 (已拦截/总异常) | 每日 | 3 层异常拦截 |
| 7 | GOV-M-007 | **sponsor_report_count** (Sponsor 报告次数) | 次 | 自动 | 阶段完成时 | Sponsor 监督 |
| 8 | GOV-M-008 | **biz_isolation_violation** (业务隔离违规) | 次 | 自动 | 每日 | 业务隔离 |

## 关键: 防止 PMO 粉饰 (Sponsor 点出)

**Sponsor 看指标看板, 不只看 PMO 报告**:
- 报告是主观 (PMO 写)
- 指标是客观 (系统跑)
- **指标可贯彻** = 跑出来, 可审计, Sponsor 可看

## 告警规则

| 指标 | 阈值 | 严重性 | 通知 |
|---|---|---|---|
| phase_gate_pass_rate < 80% | warning | pmo-instance |
| decision_log_completeness < 95% | critical | pmo-instance + sponsor |
| self_check_coverage < 90% | warning | pmo-instance |
| exception_interception_rate < 90% | critical | pmo-instance + sponsor |
| biz_isolation_violation > 0 | critical | pmo-instance + sponsor |
