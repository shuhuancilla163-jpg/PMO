# Changelog (PMO 平台变更日志)

所有重要变更记录在这里 (含规范演进, 业务接入, 重大决策)。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [0.5.0] - 2026-06-19

### Added (m1.2 合规模块, DEC-2026-0002 实施)
- scripts/runtime/compliance/compliance.py: ComplianceChecker + MetricsTraceabilityChecker
  - 5 项基础合规工具 (m1.2):
    - C11 gitleaks 密钥扫描 (AWS/GitHub/OpenAI/Private Key/Generic API Key)
    - C12 redact.py 脱敏 (email/phone/id_card/credit_card)
    - C13 数据分级检查 (4 级: public/internal/confidential/secret)
    - B13 redaction-rules 脱敏规则文档存在性
    - B14 audit-log-spec 审计日志规范
  - DEC-2026-0002 加 3 项:
    - 业务项目考核合规 (Assessor-Agent 3 维度)
    - 监控合规 (3 维度监控 + 3 告警层)
    - 消息流通合规 (Message-Broker-Agent 中介)
  - 指标可贯彻验证: MetricsTraceabilityChecker (3 件事: 可采集 + 可审计 + 可贯彻)
- docs/m1.2-compliance.md (新建, 5 项 + DEC-2026-0002 3 项 + 验收 + API)

### 验收 (7 项)
- 5 项合规工具可用 ✅
- 指标可采集 ✅
- 指标可审计 ✅
- 指标可贯彻验证可演示 ✅
- 业务项目考核合规 ✅
- 监控合规 ✅
- 消息流通合规 ✅

## [0.4.0] - 2026-06-19

### Added (m0.4 运维, DEC-2026-0002 实施)
- scripts/runtime/operations/operations.py: OperationsMonitor
  - 6 大运维能力: 监控 / 告警 3 层 / 恢复 / 灾备 / Token 预算 / 运维报告
  - 告警 3 层: biz-self / pmo / sponsor (DEC-2026-0002 边界清晰化)
  - 异常拦截 3 层: PMO 规范 / PMO 实例 / 业务项目 (DEC-2026-0002 边界)
  - 恢复 6 策略: RETRY / FALLBACK / RESTART / ROLLBACK / ESCALATE / SKIP
  - 灾备: archive/disaster-backups/<project-id>/
  - 3 维度监控: 业务项目整体 (PMO-Main) / 研发 5 阶段 (Engineer-Agent) / 业务项目上报 (Monitor-Agent)
- docs/m0.4-operations.md (新建, 6 大能力 + 验收 + API)

### 验收 (7 项)
- 监控可跑 ✅
- 告警可触发 (3 层) ✅
- 恢复可执行 ✅
- 异常拦截 3 层可演示 ✅
- Token 预算按业务项目分可验证 ✅
- 灾备可演练 ✅
- 指标监控可看 ✅

## [0.3.0] - 2026-06-19

### Added (m0.3 部署环境, DEC-2026-0002 实施)
- 本地 PMO 启动 (bash scripts/start.sh)
- Cursor harness 集成 (仓库存放 + .cursor/ 配置)
- 容器部署 (Dockerfile + docker-compose.yml, 8 PMO 角色健康检查)
- 知识存储 (12 项元规则 0.0.1-0.0.12, Git 不可变)
- 性能基线 (12 项, 8 PMO 角色 + 3 维度分离)
- docs/m0.3-deployment.md (新建, 部署架构 + 启动方式 + 验收)

### Changed
- Dockerfile: 5 agent → 8 agent 健康检查 (DEC-2026-0002)
- docker-compose.yml: 5 agent → 8 agent + PMO_ROLES_COUNT 环境变量
- start.sh: 5 agent → 8 agent 启动横幅 + 启动后状态
- perf_benchmark.py: 加 3 维度采集 + Assessor + Message-Broker 基准, psutil 可选

### 关键基线
- PMO 启动耗时基线: ~1.0ms
- 8 agent 激活基线: ~0.3ms (平均 0.04ms/agent)
- 维度 1 业务项目注册基线: 0.01ms/项目
- 维度 2 研发 5 阶段采集基线: 0.02ms/采集
- 维度 3 业务项目上报基线: 0.02ms/上报
- Assessor 3 维度考核基线: 0.08ms/考核
- Message-Broker 项目间消息基线: 0.03ms/消息
- 业务流耗时基线: ~0.1ms (10 状态转换)
- 异常拦截基线: 0.05ms/次
- 通信基线: 0.02ms/条
- 指标采集基线: 0.01ms/次
- L2 6 agent 审计 L1 基线: ~0.8ms

## [0.2.3] - 2026-06-19

### Added (m1.1 元规则, 8 → 12 项, DEC-2026-0002 实施)
- 0.0.3 价值→任务映射 (Sponsor 定的, 之前没单独文件)
- 0.0.4 价值→失败检测 (Sponsor 定的, 之前没单独文件)
- 0.0.11 业务项目 2 层合规 (DEC-2026-0002 新增)
- 0.0.12 3 维度架构 (DEC-2026-0002 新增)
- immutable/0-governance/README.md (12 项元规则索引)

## [0.2.2] - 2026-06-19

### Added (m0.2 v0.2.1, DEC-2026-0002 实施)
- 8 PMO 角色 (从 5 → 8, 按 3 维度严格分离):
  - L0 Sponsor (不变)
  - L1 PMO-Main (维度 1 业务项目整体采集)
  - L2 Plan-Agent (不变)
  - L2 Engineer-Agent (维度 2 研发 5 阶段采集)
  - L2 Monitor-Agent (新增, 维度 3 业务项目上报 + 上报合规监管)
  - L2 Reviewer-Agent (不变)
  - L2 Assessor-Agent (新增, 3 维度分别考核)
  - L2 Message-Broker-Agent (新增, 项目间消息经 PMO 中介)
- 3 维度架构 (业务项目整体 / 研发 5 阶段 / 业务项目上报)
- 业务项目 2 层合规契约 (业务项目整体 + 业务项目内研发 5 阶段)
- 3 层上报机制 (业务自采 + 业务上报 + PMO 存上报)
- 3 维度考核 (Assessor-Agent 按 3 维度分别考核)
- 项目间消息经 PMO 中介 (Message-Broker-Agent)
- 业务项目接入 PMO 5 步流程
- scripts/runtime/README.md (新建)

### Changed
- agent_base.py: 5 agent → 8 agent
- pmo_runtime.py: v0.2.0 → v0.2.1, 加 3 维度演示 + Assessor + Message-Broker

## [0.2.1] - 2026-06-18

### Added (DEC-2026-0002)

### Changed
- PMO 部署: 本地优先 (Q2)
- 不可变文档库: Git (Q4)
- 业务知识库: 接口契约, 不绑定实现 (Q3)

### Fixed
- (无)

### Removed
- (无)

## [0.1.0] - 2026-06-18

### Added
- 初始 PMO 平台搭建
- 0 章治理原则 (0.0.1 ~ 0.0.10)
- M0/M1/M2/M6/M7 任务清单 (24 任务)
- 1.1 PMO 自建项目启动
- 业务接入路径 (1 套)
- 不可变文档库 (Git)
- 决策日志 (schema + 1 决策样例)
- Memory 分级 (热/温/冷)
- 指标库 (业务/治理/工程三类)

### 关键决策
- DEC-2026-0001: PMO 1 套规范 + N 项目复用原则
