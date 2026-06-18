# 3 维度架构 (DEC-2026-0002)

**业务项目 = 1 个单位, 但 PMO 监管 3 维度** (Sponsor 平等讨论后定)

## 核心洞察

**不同维度考核指标不同 + 数据源不同, PMO 角色必须严格按 3 维度分离** (Sponsor 关键点出)。

## 3 维度架构

| 维度 | 数据源 | 谁采 (PMO 角色) | 谁存 | 谁用 |
|---|---|---|---|---|
| **维度 1: 业务项目整体** | 业务项目注册/状态/配额/归档/隔离 | **L1 PMO-Main** | PMO 存 | PMO 监管 + Sponsor 看 |
| **维度 2: 业务项目内研发 5 阶段** | 研发 5 阶段数据 (需求/研发/测试/运维/评估) | **L2 PMO-Engineer-Agent** 按阶段采 | PMO 存 (上报) + 业务项目存 (全量) | PMO 监管 + 业务项目看 |
| **维度 3: 业务项目内业务** | 业务项目按 PMO 规范上报的关键指标 | **L2 PMO-Monitor-Agent** 采上报数据 | 业务项目存业务全量 + PMO 存上报数据 | 业务项目用业务数据, PMO 监管上报合规 |

## 关键洞察 (Sponsor 推动)

### 1. 业务数据全量 = 业务项目自存 (PMO 不存)
- 业务项目 = "上市公司" (自己业务数据自己存)
- 业务数据全量 = "公司全部数据" (PMO 不存)

### 2. 业务数据上报 = 业务项目按 PMO 规范上报关键指标
- 业务项目上报 = "上市公司按 SEC 规范上报季报" (关键指标按规范上报)
- 上报数据 = "季报" (PMO 存上报数据)

### 3. PMO 监管 = 看上报数据是否合规, 不看业务具体内容
- PMO = "SEC 监管机构" (看上报数据, 不知道公司具体业务)
- PMO 监管 = "看季报是否合规" (不看具体业务)

## 3 维度采集角色严格分离

| 角色 | 采什么 | 数据源 |
|---|---|---|
| **L1 PMO-Main** | 维度 1 (业务项目整体) | register.yaml + state + quota + archive + isolation |
| **L2 PMO-Engineer-Agent** | 维度 2 (研发 5 阶段) | eng-roles/ + 5 阶段产出 + 决策日志 + 不可变文档 |
| **L2 PMO-Monitor-Agent** | 维度 3 (业务项目上报) | 业务项目按 PMO 规范上报的关键指标 |

**关键**:
- 3 维度采集**不重叠**, 严格分离
- 1 个角色只采 1 个维度 (避免混乱)
- 1 个维度只被 1 个角色采 (避免重复)

## 3 维度考核 (PMO-Assessor-Agent)

| 考核对象 | 考核内容 | 考核指标 |
|---|---|---|
| **业务项目整体** | 业务项目是否符合 PMO m2.6 7 项 | biz_project_compliance_rate, biz_project_quota_usage, ... |
| **业务项目内研发 5 阶段** | 研发 5 阶段是否符合 PMO 7 项 | requirement_phase_compliance, development_phase_compliance, ... |
| **业务项目内业务** | 业务项目是否按 PMO 规范上报 | biz_metrics_report_compliance, biz_metrics_report_timeliness, ... |

## 3 维度监控 (3 个采集角色同时是监控)

| 监控对象 | 监控方 | 监控内容 |
|---|---|---|
| **业务项目状态** | L1 PMO-Main | active/paused/blocked/completed/archived |
| **业务指标** | L2 PMO-Monitor-Agent | 5 项基础 + 业务项目自定义 |
| **业务异常** | L2 PMO-Monitor-Agent | 3 层异常拦截 |
| **业务资源** | L1 PMO-Main | 4 维配额使用率 |
| **项目间消息** | L2 PMO-Message-Broker-Agent | 数量/成功率/延迟/失败重试 |

## 业务项目 2 层合规契约

### 业务项目整体契约 (维度 1)

```yaml
project_overall_compliance:
  biz_project_id: "1.2"
  registration: "已注册到 PMO 实例"
  state_machine: "active/paused/blocked/completed/archived"
  quota_4d: ["token", "time", "storage", "concurrency"]
  archive_4_levels: ["data", "document", "project", "resource"]
  isolation_3d: ["data", "config", "state"]
  alerting_3_levels: ["biz-self", "pmo", "sponsor"]
```

### 业务项目内研发 5 阶段契约 (维度 2)

```yaml
eng_5_stages_compliance:
  requirement: { role: "Requirement-Engineer", pmo_compliance: [...] }
  development: { role: "Development-Engineer", pmo_compliance: [...] }
  test: { role: "Test-Engineer", pmo_compliance: [...] }
  operations: { role: "Operations-Engineer", pmo_compliance: [...] }
  evaluation: { role: "Evaluation-Engineer", pmo_compliance: [...] }
```

### 业务项目内业务自管 + PMO 监管上报合规契约 (维度 3)

```yaml
biz_self_managed:
  biz_flow_template: "业务项目自维护"
  biz_agent_config: "业务项目自维护 (按业务场景)"
  biz_exception_definition: "业务项目自维护"
  biz_metrics_full: "业务项目自维护 (业务全量数据)"
  biz_data_storage: "业务项目自存 (PMO 不存)"

biz_report_to_pmo:
  report_metrics_5_basic: ["flow_latency", "exception_rate", "pass_rate", "rollback_rate", "token_consumption"]
  report_metrics_custom: "业务项目自定义 (按业务场景)"
  pmo_role: "L2 PMO-Monitor-Agent 采上报数据 + 监管上报合规"
```

## 关键: 不再有的旧设计

| 旧设计 | 新设计 (DEC-2026-0002) |
|---|---|
| 8 业务 agent (PMO 预设) | 业务 agent 按业务场景配置 (业务项目自定) |
| 5 PMO agent (1 角色采 3 维度) | 8 PMO 角色 (按 3 维度严格分离) |
| 业务项目 1 层合规 | 业务项目 2 层合规 (整体 + 研发 5 阶段) |
| PMO 监管业务内容 | 业务项目自管业务, PMO 监管上报合规 |
| 业务场景由 PMO 提供模板 | 业务场景由业务项目自维护, PMO 不提供 |

## 关键决策

- **DEC-2026-0002**: 14 块关键调整 (2026-06-18)
- **影响**: m0.2/m1.3/m1.4/m1.5/m2.3/m2.5/m2.6 都要按 14 块调整实施
- **版本**: v0.2.1
