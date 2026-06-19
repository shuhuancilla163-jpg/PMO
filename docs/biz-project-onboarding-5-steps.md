# 业务项目接入 PMO 5 步流程 (DEC-2026-0002)

**业务项目接入 PMO 实例的标准流程** (Sponsor 平等讨论后定)

## 5 步流程

```
1. 业务项目注册 (m2.6 业务注册)
   ↓
2. 业务项目内研发 5 阶段声明 (m2.3 + m2.6)
   ↓
3. 业务项目内业务配置 (业务项目自管)
   ↓
4. 业务项目接入 PMO 消息机制 (m2.5 跨边界契约)
   ↓
5. 业务项目接入 PMO 监管 (m1.3 + m0.4)
```

## 第 1 步: 业务项目注册 (m0.9 OnboardingSyncer 自动化)

**业务项目填 `register.yaml`** (业务项目 ID/名称/类型/版本/Sponsor):

> **m0.9 自动化**（DEC-2026-0009）：PMO 接入时，OnboardingSyncer 自动将以下文件同步到业务项目目录，无需手动复制。

```yaml
project_id: "1.2"
name: "业务系统"
type: "biz-system"
version: "0.1.0"
status: "active"
sponsor: "Sponsor"
registered_at: "2026-06-18T17:00:00Z"
phase: "P0-init"
```

**OnboardingSyncer 接入时自动同步的文件**（业务项目注册后自动触发）：

| 同步项 | 目标路径 | 说明 |
|---|---|---|
| register.yaml | biz-projects/\<id\>/ | 业务项目注册文件 |
| 整体契约模板 | immutable/2-biz-specs/contract-\<id\>-overall.md | 整体契约 |
| 5阶段契约模板 | immutable/2-biz-specs/contract-\<id\>-eng-5-stages.md | 研发契约 |
| 业务agent契约 | immutable/2-biz-specs/contract-\<id\>-biz-ops-roles.md | 运营契约 |
| SOP 模板 | biz-projects/\<id\>/biz-docs/ | 4 类 SOP 模板 |
| 5阶段 agent 模板 | biz-projects/\<id\>/eng-roles/ | 5 阶段 agent 配置 |
| 阈值配置 | biz-projects/\<id\>/reports/thresholds.yaml | 考核阈值（可覆盖） |
| messaging.yaml | biz-projects/\<id\>/ | 消息订阅/发布配置 |
| sync-metadata.json | biz-projects/\<id\>/reports/ | 同步元数据（幂等） |

同步完成后自动记录 `reports/sync-metadata.json`，并通过 Message-Broker 通知业务项目。

```yaml
project_id: "1.2"
name: "业务系统"
type: "biz-system"
version: "0.1.0"
status: "active"
sponsor: "Sponsor"
registered_at: "2026-06-18T17:00:00Z"
phase: "P0-init"
```

**业务项目签 2 份契约**:
1. 业务项目整体契约 (`immutable/2-biz-specs/contract-<project-id>-overall.md`)
2. 业务项目内研发 5 阶段契约 (`immutable/2-biz-specs/contract-<project-id>-eng-5-stages.md`)

## 第 2 步: 业务项目内研发 5 阶段声明

**业务项目在 `eng-roles/` 声明用了哪些研发角色**:

```
biz-projects/<biz-project-id>/
├── eng-roles/
│   ├── requirement.yaml    # 需求阶段角色配置
│   ├── development.yaml    # 研发阶段角色配置
│   ├── test.yaml           # 测试阶段角色配置
│   ├── operations.yaml     # 运维阶段角色配置
│   └── evaluation.yaml     # 评估阶段角色配置
```

**业务项目可调整 5 阶段** (例如简化 2 阶段: 研发 + 运维), **但必须符合 PMO 7 项**:
- 阶段门控 (m1.3)
- 决策日志 (m1.1)
- 不可变文档 (m0.1)
- 异常拦截 (m0.4)
- 指标可贯彻 (m1.2)
- 3 层告警 (m0.4)
- Sponsor 报告 (m1.5)

## 第 3 步: 业务项目内业务配置 (业务项目自管)

**业务项目自维护** (PMO 不干预业务内容):

| 配置 | 业务项目自维护 |
|---|---|
| 业务场景 | 业务项目自选 (后期定, 不预设模板) |
| 业务 agent | 业务项目按业务场景配置 (不固定 8 个) |
| 业务流程 | 业务项目自维护 (业务流模板) |
| 业务异常 | 业务项目自定义具体业务异常 (4 类: 业务/系统/合规/性能) |
| 业务指标 | 业务项目自定义业务指标 (5 项基础 + 自定义) |
| 业务 SOP | 业务项目自维护 (Markdown) |
| 业务术语 | 业务项目自维护 |
| 业务 schema | 业务项目自维护 |
| 业务知识 | 业务项目自维护 (专有层) |
| 业务数据 | 业务项目自存 (PMO 不存) |

**关键**: 业务项目自管业务内容, PMO 不干预业务内容。

## 第 4 步: 业务项目接入 PMO 消息机制 (m2.5 + m0.9 NormPusher)

**业务项目注册时声明订阅/发布消息主题**:

```yaml
# biz-projects/<biz-project-id>/messaging.yaml
subscriptions:
  - "biz.1.1-pmo-self.state"
  - "biz.1.1-pmo-self.metric"
publications:
  - "biz.1.2-biz.state"
  - "biz.1.2-biz.metric"
```

**业务项目通过 PMO-Message-Broker-Agent 发送/接收消息**:
- 业务项目通过 PMO 实例 API 发送/接收消息
- 业务项目消息必须符合 PMO 协议
- 业务项目消息经 PMO 实例中介 (业务项目不直接通信)

## 第 5 步: 业务项目接入 PMO 监管 (m1.3 + m0.4 + m0.9)

**m0.9 考核闭环**（DEC-2026-0009）：业务项目接入后，PMO 自动开启以下考核机制：

**5.1 指标上报**

**业务项目按 PMO 规范上报关键指标**（3 类，13 项）：

| 类别 | 指标 | 方向 | warn | critical |
|---|---|---|---|---|
| 业务指标 | flow_latency（秒） | lower | 200 | 300 |
| 业务指标 | exception_rate（0~1） | lower | 0.05 | 0.20 |
| 业务指标 | pass_rate（0~1） | higher | 0.90 | 0.80 |
| 业务指标 | rollback_rate（0~1） | lower | 0.02 | 0.05 |
| 业务指标 | token_consumption（每周期） | lower | 5000 | 8000 |
| 治理指标 | decision_log_completeness | higher | 0.80 | 0.60 |
| 治理指标 | archive_completeness | higher | 0.85 | 0.70 |
| 治理指标 | state_legality_rate | higher | 0.90 | 0.70 |
| 治理指标 | quota_usage_rate | lower | 0.80 | 1.00 |
| 工程指标 | deploy_success_rate | higher | 0.95 | 0.90 |
| 工程指标 | exception_interception_rate | higher | 0.90 | 0.80 |
| 工程指标 | performance_baseline_rate | higher | 0.85 | 0.70 |
| 工程指标 | availability | higher | 0.99 | 0.95 |

上报路径：`reports/metrics.yaml`，格式 JSON，每小时上报。

**5.2 阈值考核引擎（ThresholdEngine）**

PMO 按 3 维度加权考核业务项目：

- **维度 1（权重 30%）**：治理指标（决策日志/归档/状态机/配额）
- **维度 2（权重 30%）**：工程指标（部署/异常拦截/性能基线/可用性）
- **维度 3（权重 40%）**：业务指标（流耗时/异常率/通过率/回滚率/Token消耗）

整体得分 = Σ(维度得分 × 权重)，≥90 优秀 / ≥75 良好 / ≥60 警告 / <60 违规。

**5.3 规范变更通知（NormPusher）**

运行时 PMO 监听规范目录（immutable/ + config/）变更，检测到变更后通过 Message-Broker 发 Ping 给所有 active 业务项目，业务项目主动 Pull 变更内容。定时全量同步兜底（每天凌晨）。

**PMO 监管上报合规**（3 项）：
- `biz_metrics_report_compliance`（业务指标上报合规率）
- `biz_metrics_report_timeliness`（业务指标上报及时率）
- `biz_metrics_report_completeness`（业务指标上报完整度）

**PMO 监管业务项目状态 + 业务异常**:
- L1 PMO-Main 监管业务项目状态
- L2 PMO-Monitor-Agent 监管业务异常

## 业务项目接入后, 3 维度自动接入

| 维度 | 接入内容 |
|---|---|
| **维度 1: 业务项目整体** | L1 PMO-Main 采业务项目注册/状态/配额/归档/隔离 |
| **维度 2: 业务项目内研发 5 阶段** | L2 PMO-Engineer-Agent 按 5 阶段采研发数据 |
| **维度 3: 业务项目内业务** | L2 PMO-Monitor-Agent 采业务项目上报的关键指标 |

## 业务项目接入后, 3 维度考核自动运行

| 考核对象 | 考核方 | 何时考核 |
|---|---|---|
| 业务项目整体 | L2 PMO-Assessor-Agent | 阶段完成时 |
| 业务项目内研发 5 阶段 | L2 PMO-Assessor-Agent | 每阶段完成时 |
| 业务项目内业务上报合规 | L2 PMO-Assessor-Agent | 实时 |

## 业务项目接入 PMO 后的 5 维度

| # | 维度 | 内容 |
|---|---|---|
| 1 | 业务项目整体 | 业务项目是否符合 PMO m2.6 7 项 |
| 2 | 业务项目内研发 5 阶段 | 研发是否符合 PMO 7 项 |
| 3 | 业务项目内业务 | 业务内容 (业务项目自管) |
| 4 | 业务项目内业务上报 | 业务项目是否按 PMO 规范上报 |
| 5 | 项目间消息 | 业务项目是否接入 PMO 消息机制 |

## 关键决策

- **DEC-2026-0002**: 14 块关键调整 (2026-06-18)
- **业务项目接入 PMO 5 步流程**: 业务项目接入 PMO 的标准流程
- **影响**: m2.6 业务项目管理流程更新, 业务项目模板更新
