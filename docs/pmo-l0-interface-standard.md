# PMO 层工作规范基准 (L0 Agent → PMO Instance)

**文件 ID**: `PMO-L0-INDEX`
**版本**: v0.1.0
**创建时间**: 2026-06-19
**层级**: L1 PMO 层
**接收指令来源**: L0 层 Agent

---

## 一、PMO 层职责边界

PMO 层作为 L0 层指令的执行中枢，承担以下核心职责：

| 职责 | 描述 |
|---|---|
| **指令接收** | 接收 L0 层发来的需求/任务指令 |
| **需求拆分** | 将宏观需求拆解为 PMO 实例级别的具体任务 |
| **规范制定** | 制定工作规范、标准、流程 |
| **执行监督** | 跟踪、检查、反馈执行情况 |
| **汇报反馈** | 向 L0 层汇报执行结果和状态 |

**明确边界**：
- PMO 规范不参与业务内容制定
- PMO 监管 ≠ PMO 干预
- 业务内容由业务项目自管

---

## 二、L0 → PMO 指令接口规范

### 2.1 指令格式

L0 层向 PMO 层发送的指令应包含以下字段：

```yaml
instruction:
  id: "INS-<timestamp>-<seq>"
  type: "requirement" | "task" | "decision" | "escalation" | "query"
  priority: "P0" | "P1" | "P2" | "P3"
  source: "L0"
  target: "PMO-L1"
  content:
    summary: "<指令摘要>"
    description: "<详细描述>"
    deliverables: ["<交付物1>", "<交付物2>"]
    constraints: ["<约束1>"]
    deadline: "<YYYY-MM-DD>"
  metadata:
    decision_id: "<关联决策ID>"
    project_id: "<关联项目ID>"
    phase: "<当前阶段>"
```

### 2.2 指令类型说明

| 类型 | 说明 | PMO 响应要求 |
|---|---|---|
| `requirement` | 新需求 | 拆解为任务，分配到项目 |
| `task` | 具体任务 | 直接执行或转发 |
| `decision` | 决策请求 | 记录决策日志，生成决策 |
| `escalation` | 升级请求 | 立即处理，触发告警 |
| `query` | 查询请求 | 返回状态/指标数据 |

### 2.3 PMO 响应格式

```yaml
response:
  id: "RSP-<timestamp>-<seq>"
  ref_instruction_id: "<原始指令ID>"
  status: "received" | "in_progress" | "completed" | "blocked" | "escalated"
  pmo_action:
    decomposed_tasks: ["<任务1>", "<任务2>"]
    assigned_to: "<执行方>"
    deadline: "<日期>"
    standard: "<依据的规范>"
  blockers: ["<阻碍1>"]
  metrics: "<相关指标>"
```

---

## 三、需求拆分标准流程 (5 步)

```
L0 指令输入
    ↓
[Step 1] 指令解析与分类
    ↓
[Step 2] 需求层级拆解 (Epic → Feature → Task)
    ↓
[Step 3] 任务分配与定标
    ↓
[Step 4] 执行监督计划制定
    ↓
[Step 5] 反馈与闭环
```

### Step 1: 指令解析与分类

- **解析指令类型**：`requirement` / `task` / `decision` / `escalation` / `query`
- **识别优先级**：P0 最高（立即处理）→ P3 最低
- **判断涉及维度**：维度 1（项目整体）/ 维度 2（研发 5 阶段）/ 维度 3（业务上报）

### Step 2: 需求层级拆解

按照三层结构拆解：

| 层级 | 描述 | 示例 |
|---|---|---|
| **Epic** | 大型需求单元 | "构建量化金融业务系统" |
| **Feature** | 独立功能模块 | "行情数据采集模块" |
| **Task** | 最小可执行任务 | "实现 WebSocket 行情接口" |

### Step 3: 任务分配与定标

每个 Task 必须包含：

```yaml
task:
  id: "TASK-<project>-<seq>"
  title: "<任务标题>"
  type: "requirement" | "development" | "test" | "operations" | "evaluation"
  stage: "研发5阶段对应阶段"
  priority: "P0" | "P1" | "P2" | "P3"
  assignee: "<执行agent>"
  standard_refs:
    - "m1.3"  # 核心执行规范
    - "m2.6"  # 业务项目管理
    - "m2.3"  # 研发角色规范
  deliverables: ["<交付物>"]
  deadline: "<YYYY-MM-DD>"
  gate: "<阶段门控条件>"
```

### Step 4: 执行监督计划制定

- 为每个任务制定**检查点**（Checkpoints）
- 确定**汇报周期**（小时级 / 日级 / 阶段级）
- 预设**异常处理路径**
- 明确**3 层告警规则**

### Step 5: 反馈与闭环

- 按时向 L0 层汇报进度
- 异常立即升级
- 完成后记录决策日志（m1.1）
- 更新项目状态

---

## 四、规范与标准清单

PMO 层执行任务时必须遵循以下规范：

### 4.1 PMO 7 项合规（研发 5 阶段）

| # | 规范项 | 描述 |
|---|---|---|
| 1 | 阶段门控 | 每个阶段完成后必须通过门控验收才能进入下一阶段 |
| 2 | 决策日志 | 所有重大决策必须记录到决策日志（C3） |
| 3 | 不可变文档 | 核心文档签署 Hash，存入 `immutable/` |
| 4 | 异常拦截 | 3 层异常拦截机制（业务自给 → PMO 拦截 → L0 介入） |
| 5 | 指标可贯彻 | 业务/治理/工程 3 类指标，不只报告，要落地 |
| 6 | 3 层告警 | 业务自给告警 / 重大告警→PMO / PMO→Sponsor |
| 7 | Sponsor 报告 | 关键节点必须向 Sponsor 汇报 |

### 4.2 3 维度严格分离

| 维度 | 采集方 | 数据内容 |
|---|---|---|
| **维度 1** | L1 PMO-Main | 项目整体（注册/状态/配额/归档/隔离） |
| **维度 2** | L2 Engineer-Agent | 研发 5 阶段数据 |
| **维度 3** | L2 Monitor-Agent | 业务上报指标（5 项基础 + 3 项合规） |

---

## 五、监督机制

### 5.1 监督层级

```
L0 Sponsor (监督权)
    ↓ 监督
L1 PMO-Main (行政权)
    ↓ 管理
L2 六角色 (司法权)
    ├── Plan-Agent (计划/治理)
    ├── Engineer-Agent (维度 2 采集)
    ├── Monitor-Agent (维度 3 采集)
    ├── Reviewer-Agent (审查/审计)
    ├── Assessor-Agent (3 维度考核)
    └── Message-Broker-Agent (消息中介)
```

### 5.2 监督频率

| 监督类型 | 频率 | 负责方 |
|---|---|---|
| 实时指标监控 | 每小时 | L2 Monitor-Agent |
| 阶段进度检查 | 每个阶段 | L1 PMO-Main |
| 3 维度考核 | 阶段完成时 | L2 Assessor-Agent |
| 合规审计 | 按需触发 | L2 Reviewer-Agent |
| Sponsor 汇报 | 关键节点 | L1 PMO-Main |

### 5.3 异常处理路径

```
业务层异常
    ↓ 业务项目自处理
PMO 层异常 (超过业务处理能力)
    ↓ PMO 拦截
    ├── 记录异常日志
    ├── 触发 PMO 告警
    └── 通知相关方
        ↓ 重大异常 (PMO 无法处理)
        L0 Sponsor 介入
```

---

## 六、文件与目录约定

| 路径 | 用途 |
|---|---|
| `PMO/immutable/0-governance/` | PMO 治理规范（不可变） |
| `PMO/immutable/1-pmo-specs/` | PMO 规范文档（M0/M1/M2） |
| `PMO/immutable/2-biz-specs/` | 业务项目契约 |
| `PMO/immutable/3-decisions/` | 不可变决策文档 |
| `PMO/decisions/active/` | 活跃决策日志 |
| `PMO/decisions/archive/` | 历史决策 |
| `PMO/tasks/queue/` | 任务队列 |
| `PMO/metrics/` | 指标库 |
| `PMO/reports/` | 报告输出 |
| `PMO/logs/` | 运行日志 |

---

## 七、工作状态定义

| 状态 | 含义 |
|---|---|
| `received` | 已接收指令 |
| `analyzing` | 正在解析分析 |
| `decomposing` | 正在需求拆分 |
| `in_progress` | 任务执行中 |
| `monitoring` | 监督跟踪中 |
| `blocked` | 遇到阻碍 |
| `escalated` | 已升级 L0 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |

---

## 八、版本与变更记录

| 版本 | 日期 | 变更内容 |
|---|---|---|
| v0.1.0 | 2026-06-19 | 初始建立 PMO 层工作规范基准 |
