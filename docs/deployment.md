# PMO 部署文档 (deployment.md) — v0.3.0

## 部署目标 (Q2)

| 部署目标 | 位置 | 用途 |
|---|---|---|
| **PMO 本地优先** | 当前工作目录 (workspace) | 开发环境 |
| **Cursor harness 集成** | Cursor IDE 内 | 运行时环境 |
| **容器可扩展** | Docker / docker-compose | 后期多项目 |

**业务系统** (云上自动化) — 不在本文档范围 (业务实现层, 业务项目自定)

## 部署清单

### 1. 本地部署 (开发环境)

**前置条件**:
- Python 3.9+
- Git 2.30+
- macOS / Linux / WSL2

**步骤**:

```bash
# 1. 进入 PMO 目录
cd /path/to/PMO

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 启动 PMO
bash scripts/start.sh
```

**启动后状态**:
- 5 agent 全部 running
- 1.1 业务项目 active
- 21 项指标已注册
- 性能基线已记录

### 2. Cursor harness 集成

**前置条件**:
- Cursor IDE 已安装
- Cursor 信任当前目录

**步骤**:

1. 在 Cursor 中打开 `PMO/` 目录
2. Cursor 自动识别 `AGENTS.md` (如已创建) 或 `.cursorrules` (如已创建)
3. PMO agent 通过 Cursor 调度

**关键**:
- PMO 实例**跑在本地**, Cursor 提供 harness
- 业务项目跑在云上, 通过 MCP/HTTP 契约
- Cursor 调度 5 agent, agent 协作

### 3. 容器部署 (Docker)

**前置条件**:
- Docker 20.10+
- docker-compose 2.0+

**步骤**:

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动 PMO 容器
docker-compose up -d

# 3. 查看状态
docker-compose ps
docker-compose logs pmo

# 4. 进入容器
docker exec -it pmo-instance bash

# 5. 停止
docker-compose down
```

**资源限制** (docker-compose.yml):
- CPU: 1.0 (限制), 0.25 (预留)
- 内存: 512MB (限制), 128MB (预留)

## 部署流程图

```
┌────────────────────────────────────────────────┐
│           PMO 部署流程                          │
├────────────────────────────────────────────────┤
│                                                │
│  1. 本地启动 (开发)                              │
│     bash scripts/start.sh                      │
│     ↓                                          │
│  2. Cursor harness 集成 (运行时)                 │
│     在 Cursor 中打开 PMO/                      │
│     ↓                                          │
│  3. 容器部署 (后期多项目)                        │
│     docker-compose up                          │
│     ↓                                          │
│  4. 健康检查                                    │
│     docker-compose ps                          │
│     ↓                                          │
│  5. 启动完成                                    │
│     PMO 实例: running                          │
│     5 agent: running                           │
│     1.1 业务项目: active                        │
│                                                │
└────────────────────────────────────────────────┘
```

## 启动验证 (m0.5 运行时自测)

启动后, 验证:
1. **5 agent 状态**: 全部 running
2. **1.1 业务项目状态**: active
3. **21 指标**: 已注册, 可采集
4. **3 层异常拦截**: 可演示
5. **Sponsor 通知**: 3 层可演示
6. **性能基线**: 启动耗时 < 500ms, 内存 < 100MB

## 0.0.7 解耦 + 0.0.10 1 规范 N 项目

- 1 套 PMO 规范 (0.0.1~0.0.10)
- 1 个 PMO 实例 (本地/Cursor/Docker 任意一种)
- N 个业务项目 (复用 1 套接入路径)
- **业务系统部署不在本文档** (业务实现层, 业务自定)

## 故障排查

| 故障 | 排查 |
|---|---|
| Python 找不到 | `which python3` 检查 |
| 依赖安装失败 | `pip3 install -r requirements.txt -v` |
| Git 仓库异常 | `git status` 检查, 必要时 `git fsck` |
| 容器启动失败 | `docker-compose logs pmo` 查看日志 |
| PMO 实例未起来 | 检查 `logs/pmo-startup-*.log` |
| 业务项目未注册 | 检查 `biz-projects/<biz-project-id>/register.yaml` |

## 升级路径 (后期)

1. **PMO 升级**: 用 Git tag 标记版本 (v0.1.0 → v0.2.0 → v0.3.0)
2. **业务接入**: 新业务项目复制模板, 注册到 PMO 实例
3. **跨项目**: 1 个 PMO 实例管多业务项目
4. **多实例**: 后期可多 PMO 实例 (跨域/跨云), 治理规范统一
