# Changelog (PMO 平台变更日志)

所有重要变更记录在这里 (含规范演进, 业务接入, 重大决策)。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [0.14.0] - 2026-06-19

### Added (m2.3 5 阶段 agent + m2.4 业务执行层骨架, DEC-2026-0007 框架态)

#### m2.3: 5 阶段 agent + biz-agents 骨架
- templates/eng-roles/ (7 文件, 5 份模板)
- biz-projects/1.1-pmo-self/eng-roles/ (5 agent 可激活)
- scripts/runtime/m2_3_self_test.py (25/25 pass)
- docs/m2.3-biz-agents-and-eng-roles.md (新建)

#### m2.4: 业务执行层骨架 4 项
- templates/biz-docs/ (5 份 SOP 模板)
  - 01-biz-requirements.template.md ✅
  - 02-biz-design.template.md ✅
  - 03-biz-flow.template.md ✅
  - 04-exception-handling.template.md ✅ (4 类异常)
  - 04-release-notes.template.md ✅
- 1.x-biz-template/biz-docs/03-implementation/biz-flow.md (回滚+流编排接口)
- scripts/runtime/m2_4_self_test.py (16/16 pass)

### Added (m2.5 + m2.6 业务项目)

#### m2.5: 跨边界契约骨架 3 项
- templates/ 契约模板 (J1: 3 份)
- contract-biz-external-interface.md (J2: 对外接口)
- Message-Broker-Agent + m1.6 (J3: m1.6 覆盖)
- scripts/runtime/m2_5_self_test.py (9/9 pass)

#### m2.6: 业务项目管理 14 项
- biz-data/ 归档 4 层目录 (archive/metrics/knowledge/tasks)
- scripts/runtime/m2_6_self_test.py (14/14 pass)
- docs/m2.6-biz-project-management.md

### Added (m2.6 + m2.7 接入流程)

#### m2.6: 业务项目管理 14 项
- biz-data/ 归档 4 层目录 (archive/metrics/knowledge/tasks)
- scripts/runtime/m2_6_self_test.py (14/14 pass)
- docs/m2.6-biz-project-management.md

#### m2.7: 业务项目接入流程 5 步
- docs/biz-project-onboarding-5-steps.md (5 步流程, 5254 bytes)
- scripts/runtime/m2_7_self_test.py (16/16 pass)
- docs/m2.7-biz-onboarding-5-steps.md

### Added (m2.6 + m2.7 接入流程)

#### m2.6: 业务项目管理 14 项
- biz-data/ 归档 4 层目录 (archive/metrics/knowledge/tasks)
- scripts/runtime/m2_6_self_test.py (14/14 pass)
- docs/m2.6-biz-project-management.md

#### m2.7: 业务项目接入流程 5 步
- docs/biz-project-onboarding-5-steps.md (5 步流程, 5254 bytes)
- scripts/runtime/m2_7_self_test.py (16/16 pass)
- docs/m2.7-biz-onboarding-5-steps.md

### Added (m6.1 PMO MVP 端到端)

#### m6.1: PMO MVP 端到端自测
- scripts/runtime/m6_1_self_test.py (31/31 pass)
  - M1: 阶段门控 (3/3 流转 + PhaseGateValidator)
  - M2: 3 类指标 (5+8+8=21 项 + 看板)
  - M3: 3 层异常拦截 (L2 业务 + L1 PMO)
  - M4: 3 层告警 (L1 业务自给 + L2 PMO + L3 Sponsor)
- docs/m6.1-mvp-end-to-end.md

### Verification
- m2.3 自测: 25/25 pass 100%
- m2.4 自测: 16/16 pass 100%
- m2.5 自测: 9/9 pass 100%
- m2.6 自测: 14/14 pass 100%
- m2.7 自测: 16/16 pass 100%
- m6.1 自测: 31/31 pass 100%
- m6.2 自测: 11/11 pass 100%
- M7 自测: 7/7 pass 100%
- M1.5 自检: 24/25 pass 96.0% (D20+D21+D22+D23+D24+D25 ✅)

### M7 工程实现层评估 (v0.14.0)
- docs/evaluation/ (m7.1~m7.6 6 份 JSON 报告, 共 ~21KB)
- scripts/runtime/evaluation/evaluation.py (评估框架)
- scripts/runtime/m7_self_test.py (7/7 pass)
- docs/M7-engineering-evaluation.md (汇总)





- 5 阶段 agent: 全部可实例化, stage 属性正确 ✅

### 关键决策
- **DEC-2026-0007**: 框架态重构 (2026-06-19, v0.13.1)
- m2.3: 5 阶段 agent 框架可激活, biz-agents 框架结构正确
- 框架态: PMO 只管治理骨架, 具体业务 domain 由 Sponsor 后续注入



### Added (DEC-2026-0007 框架态重构, Sponsor 反馈)

**核心修正**: 清除预置业务 agent, 改为通用骨架模板。

#### 框架态重构
- **重构前**: `1.2-finance` 预置了 6 个量化金融 agent (Quant-Analyst/Risk-Manager/Portfolio-Manager 等), 属于历史包袱
- **重构后**:
  - `1.2-finance` → `1.x-biz-template` (通用业务项目骨架模板, 框架态)
  - 量化 agent 移入 `1.x-examples/quant-finance/` (仅供参考历史示例)
  - register.yaml / data-schema.yaml / glossary.yaml 改为空模板态
  - biz-docs/ 量化内容删除, 改为框架态占位
  - biz-agents/ 目录清空, 只留 README.md 框架说明

#### 框架态原则
- **PMO 框架不管具体业务 domain**
- **具体业务 domain 由 Sponsor 后续注入**
- **1.x-examples/ 只是参考, 不是框架**

#### 自检调整
- D18 (业务元数据): 只检查 active 项目 (1.1-pmo-self), 不检查 template 项目
- D19 (业务不可变文档): 只检查 active 项目 F5 (版本管理), template 项目只检查 F1 (骨架)

### Verification
- m2.1 自测: 3/3 pass 100%
- m2.2 自测: 25/25 pass 100%
- M1.5 自检: 18/19 pass 94.7% (0 fail)

### 关键决策
- **DEC-2026-0007**: 框架态重构 (2026-06-19, v0.13.1)
- 量化 agent 从框架移到参考示例
- PMO 框架只管治理骨架, 不管具体业务实现
- 影响: m2.3/m2.4/m2.5/m2.6 全部从通用骨架出发, 不绑定量化

## [0.13.0] - 2026-06-19

### Added (m2.2 业务不可变文档 2 项, DEC-2026-0006, 16 → 17 元规则)

**核心完成**: M2 业务基础设施第二项, 业务产出文档规范化 + 版本化管理。

#### 元规则 (16 → 17)
- immutable/0-governance/0.0.17-biz-immutable-docs.md (新建)
  - F1: 4 类业务文档骨架 (01-requirements/ / 02-design/ / 03-implementation/ / 04-release/)
  - F5: Git tag/release + semver 版本管理
  - 两层不可变文档分离 (PMO 治理 vs 业务产出)
  - biz-docs 与 5 阶段研发的关系
- immutable/0-governance/README.md (更新, 17 项元规则索引)

#### 业务不可变文档 2 项 (m2.2)
- scripts/runtime/biz_version_store/biz_version_store.py (新建, 260 行)
  - BizVersionStore: 业务项目版本管理
  - release() / next_minor() / next_major()
  - parse_tag() 支持含 . 的 biz_id (如 1.2-finance)
  - compare_versions() semver 比较
  - 版本存储: config/biz-meta/<id>-versions.json
- scripts/runtime/biz_version_store/m2_2_self_test.py (新建)
  - F1: 业务不可变文档骨架 18/18 pass
  - F5: 版本管理 14/14 pass
  - 输出 tests/m2.2-self-test-report.json
- biz-projects/1.2-finance/biz-docs/ (新建, 8 文件)
  - 01-requirements/biz-requirements.md (1715 bytes)
  - 02-design/biz-design.md + api-contract.md
  - 03-implementation/biz-flow.md + exception-handling.md
  - 04-release/release-notes.md + deployment.md
- biz-projects/1.1-pmo-self/biz-docs/ (新建, 4 文件)
  - biz-requirements.md + biz-design.md + biz-flow.md + release-notes.md
- biz-projects/templates/biz-docs/README.md (新建)
  - 业务项目 biz-docs 使用模板
- scripts/runtime/self_check/self_check.py (更新)
  - D19 业务不可变文档自检
  - 18/19 pass 94.7%
- docs/m2.2-biz-immutable-docs.md (新建)
  - F1 文档骨架验收 + F5 版本管理验收 + 两层分离 + 与 m2.1 关系

#### 决策 + 版本
- decisions/active/DEC-2026-0006.json (新建)
  - 4 块关键设计: F1/F5 + 两层分离 + biz-docs 与 5 阶段关系
  - release_version: v0.13.0

### Changed
- 16 元规则 → 17 元规则 (新增 0.0.17)
- 业务产出文档规范化 (biz-docs/ 4 类)

### Verification
- m2.2 自测: 32/32 pass 100%
- M1.5 自检: 18/19 pass 94.7% (D19 接入 ✅)
- biz-docs 文档: 1.1 (4 篇) + 1.2 (8 篇) 全部存在
- semver 演进: v1.0.0 → v1.0.1 → v1.1.0 → v2.0.0 正确

### 关键决策
- **DEC-2026-0006**: 业务不可变文档 2 项 (2026-06-19, v0.13.0)
- F1: 4 类文档骨架 (需求/设计/实施/发布)
- F5: Git tag/release + semver 版本管理
- 两层分离: PMO 治理不可变 vs 业务产出不可变
- 影响: m2.4 业务 SOP (biz-flow.md) / m2.5 跨边界契约 (api-contract.md)



### Added (m2.1 业务元数据 3 项, DEC-2026-0005, 15 → 16 元规则)

**核心完成**: M2 业务基础设施第一项, 业务接入 5 步流程前 3 步基于 m2.1。

#### 元规则 (15 → 16)
- immutable/0-governance/0.0.16-biz-metadata-3-items.md (新建)
  - E1 业务项目元数据 (register.yaml 必填字段)
  - E2 业务数据 schema (业务项目定义, PMO 存 + 验证)
  - E3 业务术语表 (业务 agent 定义, PMO 验证)
  - 业务 agent role 不与 5 阶段研发 role 重名 (DEC-2026-0003 边界)
- immutable/0-governance/README.md (更新, 16 项元规则索引)

#### 业务元数据 3 项 (m2.1)
- scripts/runtime/biz_metadata/biz_metadata.py (新建, 590 行)
  - E1 业务项目元数据 (BizMetadataStore.load_e1): 6 大块必填字段验证
  - E2 业务数据 schema (load_e2): entities + events 验证
  - E3 业务术语表 (load_e3): terms + roles 验证 + role 边界
  - 内置简化 YAML 解析器 (不依赖 pyyaml)
  - PMO 存 config/biz-meta/<id>*.json
- scripts/runtime/biz_metadata/m2_1_self_test.py (新建)
  - 3 项验收点 (按 plan)
  - 输出 tests/m2.1-self-test-report.json
- scripts/runtime/self_check/self_check.py (更新)
  - D18 业务元数据 3 项自检接入
  - 17/18 pass 94.4%
- docs/m2.1-biz-metadata.md (新建)
  - 验收 3 项 + E1/E2/E3 规范 + 5 阶段研发 agent 边界 + PMO 存储位置

#### 业务项目元数据补全
- biz-projects/1.1-pmo-self/data-schema.yaml (新建, 3 实体: task/decision/metric)
- biz-projects/1.1-pmo-self/glossary.yaml (新建, 7 术语 + 5 业务 agent role)
- biz-projects/1.2-finance/data-schema.yaml (新建, 4 实体: order/trade/position/risk_metric)
- biz-projects/1.2-finance/glossary.yaml (新建, 8 术语 + 6 业务 agent role)
- biz-projects/1.1-pmo-self/register.yaml (升级到 m2.1 嵌套规范)
- biz-projects/1.2-finance/register.yaml (升级到 m2.1 嵌套规范)

#### 决策 + 版本
- decisions/active/DEC-2026-0005.json (新建)
  - 3 块关键设计: E1 业务项目元数据 + E2 业务数据 schema + E3 业务术语表
  - release_version: v0.12.0

### Changed
- 15 元规则 → 16 元规则 (新增 0.0.16)
- 1.1/1.2 业务项目 register.yaml 升级到 m2.1 嵌套规范
- 业务项目接入 5 步流程前 3 步基于 m2.1 完整实施

### Verification
- m2.1 自测: 3/3 pass 100%
- m1.5 自检: 17/18 pass 94.4% (D18 接入, 0 fail)
- 2 个业务项目 (1.1 + 1.2) 全部成功接入 PMO 实例
- 6 个 PMO 存储文件 (config/biz-meta/)
- 11 个业务 agent role 全部不与 5 阶段研发 role 重名

### 关键决策
- **DEC-2026-0005**: 业务元数据 3 项 (2026-06-19, v0.12.0)
- 业务项目自定, PMO 存 + 验证
- 不参与业务数据, 只管元数据
- 影响: m2.6 注册 + m2.5 契约 + m2.4 执行

## [0.11.0] - 2026-06-19

### Added (m1.6 项目间消息流通, DEC-2026-0004, 14 → 15 元规则)

**核心完成**: M1 规则 6 项全闭环 (m1.1-m1.6), 业务接入第 4 步 (消息接入) 有完整实现。

#### 元规则 (14 → 15)
- immutable/0-governance/0.0.15-inter-biz-messaging.md (新建)
  - 业务项目↔业务项目消息经 PMO 实例中介
  - 6 类消息类型 (request/response/notification/alert/escalation/biz_event/biz_data)
  - 6 类主题 (biz.* + inter.biz.* + pmo.*)
  - 3 类 QoS (0/1/2)
  - 11 项监控指标
  - append-only 审计日志
  - 重试策略 (4 次退避)
  - 协议强制字段校验
- immutable/0-governance/README.md (更新, 15 项元规则索引)

#### Message-Broker 完整化 (m1.6)
- scripts/runtime/protocol/message_broker.py (新建, 340 行)
  - 6 类 MessageType 枚举
  - 3 类 QoSLevel 枚举
  - 主题 6 类正则模式 (TOPIC_PATTERNS)
  - 协议强制字段 (msg_id/msg_type/from/to/topic/qos/timestamp/layer/content)
  - 协议校验 (validate 方法)
  - 11 项监控指标 (stats)
  - append-only 审计日志 (logs/message-broker/audit-YYYYMMDD.log)
  - 重试机制 (4 次退避: 100ms/500ms/2s/10s)
  - 中介路由 (业务项目 A → broker → 业务项目 B)
- scripts/runtime/agents/agent_base.py (更新)
  - MessageBrokerAgent 委托 m1.6 MessageBroker
  - 7 个 action 接口: subscribe/unsubscribe/publish/deliver/get_message_stats/get_monitoring_metrics/get_audit_log
- scripts/runtime/m1_6_self_test.py (新建)
  - 5 项验收点 (按 plan + 0.0.15)
  - 输出 tests/m1.6-self-test-report.json
- scripts/runtime/self_check/self_check.py (更新)
  - D17 消息流通自检 (4 子检查: 路由/协议/监控/审计)
  - 16/17 pass 94.1%
- docs/m1.6-message-broker.md (新建)
  - 验收 5 项 + 6 类类型 + 6 类主题 + 3 类 QoS + 11 项监控 + 重试 + 审计

#### 决策 + 版本
- decisions/active/DEC-2026-0004.json (新建)
  - 4 块关键设计: 协议强制 + 中介路由 + 可靠性 + 可监控可审计
  - release_version: v0.11.0

### Changed
- 14 元规则 → 15 元规则 (新增 0.0.15)
- 业务接入第 4 步 (消息接入) 完整实现
- Message-Broker-Agent 从 m0.2 简化版升级到 m1.6 完整版

### Verification
- m1.6 自测: 5/5 pass 100%
- m1.5 自检: 16/17 pass 94.1% (含 D17)
- m0.5 自测: 12/12 pass 100%
- PMO 运行时: 8 agent 集成无破坏
- Sponsor 通知: D17 自检结果进 Sponsor 看板

### 关键决策
- **DEC-2026-0004**: 项目间消息流通 (2026-06-19, v0.11.0)
- 业务项目不直接通信, 全部经 PMO broker
- 消息可监控/可审计, 决策日志规范
- 影响: m2.5 跨边界契约加项目间消息契约

## [0.10.0] - 2026-06-19

### Added (DEC-2026-0003 5 阶段 agent 修正, 12 → 14 元规则)

**核心修正**: 5 阶段 agent 物理位置移到业务项目内, PMO 只给初始模板 + 规范 + 监督

#### 元规则 (12 → 14)
- immutable/0-governance/0.0.11-biz-project-2layer-compliance.md (更新)
  - 第 37 行 "PMO 预设" → "PMO 给初始模板, 业务项目实施/调整"
  - 加 "业务项目内 2 类 agent 边界" 段
- immutable/0-governance/0.0.12-3dimension-architecture.md (更新)
  - 维度 2: 5 阶段 agent 物理位置在业务项目内, PMO 采上报数据
  - 加 "5 阶段 agent 物理位置 (DEC-2026-0003)" 关键洞察
- immutable/0-governance/0.0.13-eng-5-stages-spec.md (新建)
  - 5 阶段 agent 输入输出规范
  - 5 阶段 (requirement/development/test/operations/evaluation) 通用接口
  - PMO 7 项合规清单
  - 业务项目可调但不可减
- immutable/0-governance/0.0.14-biz-ops-roles-self-define.md (新建)
  - 业务需求运营 agent 业务项目自定原则
  - PMO 不预设不干预 (不固定 8 个)
  - 业务 agent vs 5 阶段 agent 边界
- immutable/0-governance/README.md (更新, 14 项元规则索引)

#### PMO 5 阶段初始模板 (新建, 8 文件)
- templates/eng-roles/README.md (模板使用说明)
- templates/eng-roles/01-requirement-engineer.template.md
- templates/eng-roles/02-development-engineer.template.md
- templates/eng-roles/03-test-engineer.template.md
- templates/eng-roles/04-operations-engineer.template.md
- templates/eng-roles/05-evaluation-engineer.template.md
- templates/eng-roles/eng-roles-register.template.yaml
- templates/eng-roles/pmo-7-compliance-check.template.md

#### 业务项目演示 (DEC-2026-0003 5 阶段修正后)
- biz-projects/1.1-pmo-self/eng-roles/ (新建, 7 文件)
  - 5 阶段 agent (.py) + register.yaml + README.md
  - 演示: PMO 自建项目从 PMO 模板复制 + 业务调整
- biz-projects/1.2-finance/ (新建, 完整业务项目)
  - 5 阶段 agent (eng-roles/, 7 文件) — 业务调整 (Python + 量化库)
  - 6 业务 agent (biz-agents/, 7 文件) — 业务项目自定 (Data-Engineer/Quant-Analyst/Risk-Manager/Portfolio-Manager/Compliance-Officer/Reporting-Analyst)
  - reports/ (3 上报文件)
  - biz-data/ (业务数据自存, PMO 不存)

#### 业务项目契约模板 (更新 + 新建)
- biz-projects/templates/contract-eng-5-stages.md (更新, 引用 0.0.13)
- biz-projects/templates/contract-project-overall.md (更新, 加 2 类 agent 边界)
- biz-projects/templates/contract-biz-ops-roles.md (新建, 业务 agent 契约)
- biz-projects/templates/README.md (更新, 3 契约模板 + 接入流程调整)

#### 配置 + 代码 + 文档 (更新)
- config/pmo.config.yaml (更新)
  - 5 阶段实施位置: biz-projects/<id>/eng-roles/
  - 模板源: PMO/templates/eng-roles/
  - 元规则引用: 0.0.13 + 0.0.14
  - 业务 agent 位置: biz-projects/<id>/biz-agents/ (业务自管)
  - biz-projects 列表: 1.2-finance 改为 active (演示业务项目)
- scripts/runtime/agents/agent_base.py (更新)
  - Engineer-Agent 注释加 "5 阶段 agent 物理位置在业务项目内, PMO 采上报"
  - collect_eng_stage_data / get_eng_5_stages_status docstring 更新
- docs/m1.4-8-pmo-roles.md (更新, 8 PMO 角色 + DEC-2026-0003 关键说明)

#### 决策 + 版本
- decisions/active/DEC-2026-0003.json (新建)
  - 5 阶段 agent 修正决策
  - 4 块关键调整: 物理位置 + PMO 不实施 + 业务项目可调 + 业务 agent 自定
  - 12 → 14 元规则
  - release_version: v0.10.0

### Changed
- 12 元规则 → 14 元规则 (新增 0.0.13 + 0.0.14)
- 5 阶段 agent 物理位置: 业务项目内 (`eng-roles/`)
- 业务项目接入 5 步流程: 加 5 阶段 agent 从 PMO 模板复制 + 调整

### Key Decisions
- **DEC-2026-0003**: 5 阶段 agent 修正 (2026-06-19, v0.10.0)
- 5 阶段 agent 在业务项目内实施
- PMO 不实施 5 阶段 agent, 只给模板 + 规范 + 监督
- 业务需求运营 agent 业务项目自定 (0.0.14, PMO 不预设不干预)

## [0.9.0] - 2026-06-19

### Added (m1.5 PMO 自检, 9 项 + DEC-2026-0002 3 项 + 4 项机制)
- scripts/runtime/self_check/self_check.py: SelfChecker
  - 9 项基础自检 (m1.5):
    - D1 阶段流转合规
    - D2 阶段门控生效
    - D3 不可变文档完整性
    - D4 接口契约一致性
    - D10 跨级汇报检测
    - D11 主 agent 越权检测
    - D12 子 agent 决策越权检测
    - D13 异常拦截检测
    - D16 指标可贯彻检测
  - DEC-2026-0002 加 3 项:
    - 业务项目考核自检 (Assessor-Agent 3 维度)
    - 3 维度监控自检 (PMO-Main/Engineer/Monitor)
    - 消息流通自检 (Message-Broker 3 步)
  - 4 项机制:
    - PMO 升级机制 (不可变文档签名 sha256)
    - Sponsor 报告可出
    - 自进化机制 (ReflectionManager 0.0.8)
    - 指标看板可看
- tests/m1.5-self-check-report.json (新建, 15/16 pass 93.8%)
- docs/m1.5-self-check.md (新建, 9 项 + DEC-2026-0002 3 项 + 4 项机制 + 验收 + API)

### 自检结果
- 15/16 pass (93.8%), 1 项警告 (D16 路径)

## [0.8.0] - 2026-06-19

### Added (m1.4 8 PMO 角色规范, DEC-2026-0002 5 → 8)
- docs/m1.4-8-pmo-roles.md (新建, 8 PMO 角色规范 + 3 维度 + 三权分立)
- 代码已在 m0.2 v0.2.1 实施 (agent_base.py)
- 8 PMO 角色:
  - L0 Sponsor (人机, 监督权, 顶层权威)
  - L1 PMO-Main (行政权, 1 实例管 N 项目, 维度 1 业务项目整体采集)
  - L2 Plan-Agent (司法权, 计划/治理, 审计 L1)
  - L2 Engineer-Agent (司法权, 工程, 维度 2 研发 5 阶段采集)
  - L2 Monitor-Agent (司法权, 监控, 维度 3 业务项目上报) [新]
  - L2 Reviewer-Agent (司法权, 审查/审计, 互相验证)
  - L2 Assessor-Agent (司法权, 考核, 3 维度分别考核) [新]
  - L2 Message-Broker-Agent (司法权, 消息, 项目间消息经 PMO 中介) [新]

### 验收 (4 项)
- 8 agent 可激活 (L0/L1/L2×6) ✅
- 三权分立可演示 ✅
- 1 规范 N 项目可演示 ✅
- 3 维度采集严格分离 ✅

## [0.7.0] - 2026-06-19

### Added (m1.3 核心执行, 7 项工具 + DEC-2026-0002 2 项)
- scripts/runtime/core_execution/core_execution.py:
  - C1 阶段流转引擎 (P0-P9 状态机) PhaseFlowEngine
  - C2 阶段门控验收 PhaseGateValidator
  - C3 决策日志工具 (SQLite) DecisionLog
  - C6 不可变文档签名 (Git + sha256) ImmutableDocSigner
  - C9 Sponsor 介入面板 SponsorDashboard
  - C10 角色性格 prompt 加载器 PersonalityLoader
  - C15 角色身份加载器 (含 L? 注入) RoleIdentityLoader
  - DEC-2026-0002: 3 维度分别考核 (Assessor-Agent) ThreeDimensionAssessment
  - DEC-2026-0002: 3 维度监控 ThreeDimensionMonitor
- decisions/decision-log.db (新建, SQLite 决策日志)
- docs/m1.3-core-execution.md (新建, 7 项 + DEC-2026-0002 2 项 + 验收 + API)

### 验收 (5 项)
- 7 项核心执行可跑 ✅
- 业务/治理/工程指标可采 ✅
- PMO 规范不参与业务可验证 ✅
- 3 维度分别考核 ✅
- 3 维度监控 ✅

## [0.6.0] - 2026-06-19

### Added (m0.5 运行时自测, 12 项 100% pass, DEC-2026-0002)
- scripts/runtime/pmo_self_test.py: SelfTest
  - 12 项自测 (用 mock 数据验证)
  - [1] PMO 实例能起来
  - [2] 8 PMO 角色能激活
  - [3] 状态机能跑
  - [4] 状态能持久化
  - [5] 业务项目能注册
  - [6] 3 维度能采集
  - [7] Assessor 能考核
  - [8] Message-Broker 能投递
  - [9] 触发器能触发
  - [10] 异常能拦截
  - [11] 指标能跑批
  - [12] 反射能记录
- tests/m0.5-self-test-report.json (新建, 12/12 pass 100.0%)
- docs/m0.5-self-test.md (新建, 12 项 + 验收 + API)

### 验收 (4 项)
- PMO 能起来 ✅
- agent 能激活 ✅
- 状态能持久化 ✅
- 用 mock 数据验证 ✅

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
