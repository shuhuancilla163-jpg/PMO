# 业务项目整体契约模板 (DEC-2026-0002)

**业务项目接入 PMO 实例时必签契约 1: 业务项目整体契约**

业务项目 ID: `<biz-project-id>`
业务项目名称: `<biz-project-name>`
业务项目类型: `<biz-project-type>`
版本: `<biz-project-version>`
Sponsor: `<sponsor-name>`
注册时间: `<registered-at>`

## 业务项目整体符合 PMO (m2.6 7 项)

### 1. 业务项目注册
- 业务项目 ID 唯一
- 业务项目名称/类型/版本/Sponsor 完整
- 业务项目 register.yaml 已创建

### 2. 业务项目状态机
- 状态: `registered` / `active` / `paused` / `blocked` / `completed` / `archived` / `canceled`
- 状态转换合法 (符合状态机规则)
- 状态机历史可追溯

### 3. 业务项目配额 (4 维)
- `token`: Token 配额
- `time`: 时间配额
- `storage`: 存储配额
- `concurrency`: 并发配额
- 配额可监控 (L1 PMO-Main 监管)
- 配额 80% 警告, 100% critical

### 4. 业务项目归档 (4 层面)
- `data`: 数据归档
- `document`: 文档归档
- `project`: 项目归档
- `resource`: 资源释放
- 归档完整度可考核 (L2 PMO-Assessor-Agent 考核)

### 5. 业务项目隔离 (3 维)
- `data`: 数据隔离 (全隔离, 不跨项目访问)
- `config`: 配置隔离 (业务项目配置独立)
- `state`: 状态隔离 (业务项目状态独立)
- 隔离违规 0 次

### 6. 业务项目告警 (3 层)
- `biz-self`: 业务自给 (业务项目自处理)
- `pmo`: 重大→PMO (升级到 PMO 实例)
- `sponsor`: PMO 重大→Sponsor (升级到 Sponsor)

## 业务项目维度 1 考核 (L2 PMO-Assessor-Agent)

业务项目整体被 PMO 考核, 考核指标:
- `biz_project_compliance_rate` (合规率)
- `biz_project_quota_usage` (配额使用率, 4 维)
- `biz_project_state_legality` (状态合法性)
- `biz_project_archive_completeness` (归档完整度)
- `biz_project_isolation_violation` (隔离违规)
- `biz_project_alert_count` (告警次数)

## 业务项目维度 1 监控 (L1 PMO-Main)

业务项目整体被 PMO 监控:
- 业务项目状态变化 (active/paused/blocked/completed/archived)
- 业务项目配额使用率 (4 维)
- 业务项目隔离违规 (0 容忍)

## 业务项目维度 1 契约生效条件

业务项目整体契约生效:
- 业务项目 register.yaml 已创建
- 业务项目状态机可运行
- 业务项目配额 4 维可配
- 业务项目归档 4 层面可演示
- 业务项目隔离 3 维可验证
- 业务项目告警 3 层可演示

## 业务项目维度 1 契约违反处理

| 违反 | 处理 |
|---|---|
| 业务项目注册违规 | 拒绝注册 |
| 业务项目状态机非法 | 状态告警 + 强制恢复 |
| 业务项目配额超限 | 警告 + critical + 业务项目暂停 |
| 业务项目归档不完整 | 考核扣分 + 告警 |
| 业务项目隔离违规 | critical + 升级到 Sponsor |
| 业务项目告警失败 | 告警通道修复 + 重新告警 |

## 业务项目整体契约签署

业务项目接入 PMO 时, 业务项目必须签本契约, 业务项目代表:
```
业务项目代表: ___________ (签名)
PMO 实例: PMO-Main (Sponsor 授权)
日期: ___________
```
