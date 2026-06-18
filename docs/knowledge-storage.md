# 知识存储方案 (0.0.7 + Q3 + Q4 + Q27)

## 总览

PMO 知识存储 = **Git (不可变 + 版本) + 本地文件 (业务知识 2 层)**, 满足:
- **Q4**: 不可变文档库 = Git
- **Q3**: 业务知识库 = 接口契约, 不绑定实现
- **Q27**: 业务知识库 = 通用共享 + 业务专有 2 层
- **0.0.7**: 治理不绑工程, Git 是工程实现层选择, 可换

## 存储分层

### 1. 不可变文档库 (Git, 本地仓库)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `immutable/0-governance/` | 0.0.1~0.0.10 治理原则 | PMO 全部 | 只追加, 不修改 |
| `immutable/1-pmo-specs/` | PMO 规范 (M0/M1/M2/M6/M7) | PMO 全部 | 只追加, 不修改 |
| `immutable/2-biz-specs/` | 业务项目规范 (业务接入契约) | PMO + 业务项目 | 只追加, 不修改 |
| `immutable/3-decisions/` | 不可变决策文档 | PMO 全部 | 只追加, 不修改 |
| `immutable/4-templates/` | 不可变模板 (业务项目模板骨架) | PMO 全部 | 只追加, 不修改 |

**关键**:
- Git 跟踪, commit 历史, tag/release
- **不可修改**, 只追加
- 修改需走决策流程 (P9 授权 + 决策日志)

### 2. 业务知识库 (2 层)

#### 通用层 (`biz-knowledge/general/`)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `terms/` | 通用术语 | 所有业务项目 | PMO 评审后追加 |
| `specs/` | 通用规范引用 | 所有业务项目 | PMO 评审后追加 |
| `sop-templates/` | 通用 SOP 模板 | 所有业务项目 | PMO 评审后追加 |
| `contract-templates/` | 通用契约模板 | 所有业务项目 | PMO 评审后追加 |

**关键**:
- 所有业务项目**只读**
- PMO 实例评审后追加
- Git 跟踪, 变更走决策流程

#### 专有层 (`biz-knowledge/specific/<biz-project-id>/`)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `terms.md` | 业务专有术语 | 仅本项目 | 业务项目自定 |
| `data-schema.md` | 业务数据 schema | 仅本项目 | 业务项目自定 |
| `sop/` | 业务专有 SOP | 仅本项目 | 业务项目自定 |
| `best-practices/` | 业务专有最佳实践 | 仅本项目 | 业务项目自定 |

**关键**:
- 业务项目**自管** (项目实现层)
- PMO 不干预内容
- PMO 可验证是否符合契约 (m1.2)

### 3. 决策日志 (Git, append-only)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `decisions/active/` | 当前生效决策 | PMO 全部 + Sponsor | 只追加 |
| `decisions/archive/` | 历史决策 | PMO 全部 + Sponsor | 只追加 |
| `decisions/schema.json` | 决策日志 schema | PMO 全部 | 只追加 |

### 4. 指标库 (Git + 运行时文件)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `metrics/schema.json` | 指标 schema (业务/治理/工程) | PMO 全部 | 评审后追加 |
| `metrics/business/README.md` | 业务指标定义 | PMO 全部 | 评审后追加 |
| `metrics/business/<biz-project-id>/` | 业务项目指标 (运行时) | PMO 实例 + 本项目 | 自动生成 |
| `metrics/governance/README.md` | 治理指标定义 | PMO 全部 | 评审后追加 |
| `metrics/engineering/README.md` | 工程指标定义 | PMO 全部 | 评审后追加 |
| `metrics/engineering/<biz-project-id>/` | 工程指标 (运行时) | PMO 实例 + 本项目 | 自动生成 |

**关键**:
- 运行时指标 (`.gitignore` 排除 `metrics/runtime/`)
- 历史指标进 Git (业务/治理/工程/<biz-project-id>/)

### 5. Memory 分级 (0.0.2 工程化)

| 级别 | 路径 | 访问频率 | 持久化 |
|---|---|---|---|
| 热 | `memory/hot/` | 实时 | 内存 + 临时文件 (`.gitignore`) |
| 温 | `memory/warm/` | 近期 | Git 跟踪 |
| 冷 | `memory/cold/` | 历史 | Git 跟踪 |

### 6. 任务状态 (Git + 临时)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `tasks/state/<biz-project-id>.json` | 业务项目状态机 | PMO 实例 | 自动生成 |
| `tasks/queue/` | 任务队列 (active/processing/done) | PMO 实例 | 自动生成 |
| `tasks/schema.json` | 任务 schema | PMO 全部 | 评审后追加 |

### 7. 业务项目 (Git, 项目隔离)

| 路径 | 内容 | 访问 | 修改 |
|---|---|---|---|
| `biz-projects/1.1-pmo-self/` | 1.1 PMO 自建 (当前) | PMO 实例 + 本项目 | 项目内可改 |
| `biz-projects/1.2-biz/` | 1.2 业务 (1.1 完成后) | PMO 实例 + 本项目 | 项目内可改 |
| `biz-projects/templates/` | 业务项目模板 | PMO 实例 | 评审后追加 |

**关键**:
- 每个业务项目独立子目录
- 项目内可改, 项目间隔离
- PMO 实例管注册/状态/配额/归档

## 0.0.7 解耦

| 层 | 存储 | 工程实现选择 |
|---|---|---|
| 价值层 | (不变) | - |
| 治理层 | (规范) | - |
| 工程实现层 | **Git + 本地文件** | M7 评估其他 (DB/向量库/混合) |
| 项目实现层 | 业务项目自定 | 业务项目可换 |

## 0.0.7 + Q2 关注

- **知识存储**: Git 仓库, 增量保存, commit 历史
- **性能**: Git 操作 (commit/branch/diff) 毫秒级, 不影响运行时
- **网络**: PMO 本地, 无网络依赖 (业务系统云上, 远程契约)
- **可扩展**: 后期可换存储 (M7 选型时), 不影响治理层

## 关键: 1 套存储, N 项目复用 (0.0.10)

- 1 套知识存储方案 (Git + 本地文件)
- 1 个 PMO 实例
- N 个业务项目 (每个项目独立子目录, 复用 1 套存储)
- **不用为每个项目建独立存储**
