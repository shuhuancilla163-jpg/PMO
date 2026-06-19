# 业务项目 1.1-pmo-self eng-roles/

**业务项目 1.1-pmo-self 内部研发 5 阶段 agent** (DEC-2026-0003, 5 阶段 agent 物理位置在业务项目内)

## 5 阶段 agent 清单

| # | 阶段 | 文件 | 必选 | 状态 |
|---|---|---|---|---|
| 1 | Requirement-Engineer | [01-requirement-engineer.py](./01-requirement-engineer.py) | 否 | 已实施 |
| 2 | Development-Engineer | [02-development-engineer.py](./02-development-engineer.py) | **是** | 已实施 |
| 3 | Test-Engineer | [03-test-engineer.py](./03-test-engineer.py) | **是** | 已实施 |
| 4 | Operations-Engineer | [04-operations-engineer.py](./04-operations-engineer.py) | **是** | 已实施 |
| 5 | Evaluation-Engineer | [05-evaluation-engineer.py](./05-evaluation-engineer.py) | 否 | 已实施 |

## 5 阶段 agent 实施

业务项目 1.1-pmo-self 从 PMO 模板复制 + 调整:
- 模板来源: `PMO/templates/eng-roles/`
- 元规则: 0.0.13
- 业务项目定制: PMO 自建项目特点 (8 PMO 角色 + 3 维度架构 + Docker 部署)

## PMO 监督

PMO L2 Engineer-Agent 监督:
- 5 阶段上报数据是否符合 PMO 7 项合规
- 决策日志完整性
- 不可变文档数量
- 异常拦截率

**PMO 不监督**:
- 5 阶段 agent 具体实现代码
- 5 阶段 agent 业务特定工具
- 5 阶段 agent 业务特定输入输出字段

## 注册

业务项目 1.1-pmo-self eng-roles/ 注册见 [register.yaml](./register.yaml)

## 关键

- **5 阶段 agent 物理位置在业务项目内** (DEC-2026-0003)
- **PMO 给模板, 业务项目实施**
- **必选阶段 (研发/测试/运维) 不可关闭**
- **PMO 7 项合规检查项不可减少**
- **业务项目上报 PMO 监督**
