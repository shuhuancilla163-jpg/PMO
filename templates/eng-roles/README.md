# PMO 5 阶段初始模板 (PMO 给业务项目参考)

**业务项目接入 PMO 时, 5 阶段 agent 从本目录复制到 `biz-projects/<biz_project_id>/eng-roles/`, 然后按业务调整实施**

**元规则**: 0.0.13-eng-5-stages-spec.md (DEC-2026-0003)

## 5 阶段模板清单

| # | 文件 | 阶段 | 必选 |
|---|---|---|---|
| 1 | [01-requirement-engineer.template.md](./01-requirement-engineer.template.md) | 需求 | 否 (可关闭) |
| 2 | [02-development-engineer.template.md](./02-development-engineer.template.md) | 研发 | **是 (必选)** |
| 3 | [03-test-engineer.template.md](./03-test-engineer.template.md) | 测试 | **是 (必选)** |
| 4 | [04-operations-engineer.template.md](./04-operations-engineer.template.md) | 运维 | **是 (必选)** |
| 5 | [05-evaluation-engineer.template.md](./05-evaluation-engineer.template.md) | 评估 | 否 (可关闭) |

## 辅助文件

| 文件 | 作用 |
|---|---|
| [eng-roles-register.template.yaml](./eng-roles-register.template.yaml) | 业务项目 eng-roles/ 注册模板 |
| [pmo-7-compliance-check.template.md](./pmo-7-compliance-check.template.md) | PMO 7 项合规检查模板 |

## 业务项目使用流程

```bash
# 1. 业务项目接入 PMO, 创建 eng-roles/ 目录
mkdir -p biz-projects/<biz_project_id>/eng-roles/

# 2. 从 PMO 模板复制 5 阶段 agent
cp PMO/templates/eng-roles/01-requirement-engineer.template.md \
   biz-projects/<biz_project_id>/eng-roles/01-requirement-engineer.py

cp PMO/templates/eng-roles/02-development-engineer.template.md \
   biz-projects/<biz_project_id>/eng-roles/02-development-engineer.py

# ... 其他 3 个阶段

# 3. 复制注册模板
cp PMO/templates/eng-roles/eng-roles-register.template.yaml \
   biz-projects/<biz_project_id>/eng-roles/register.yaml

# 4. 业务项目按业务调整 5 阶段 agent
#    - 可简化/扩展
#    - 可加业务特定工具
#    - 但必选阶段不可关闭
#    - PMO 7 项合规检查项不可减少

# 5. 业务项目实施 5 阶段 agent 代码
#    - 实施 define_inputs/define_outputs/execute/report_to_pmo

# 6. 业务项目接入 PMO 5 步流程
#    - 注册到 PMO
#    - 签 2 份契约 (project-overall + eng-5-stages)
#    - 接入 PMO 消息机制
#    - 上报 5 阶段数据
```

## PMO 职责

PMO **只提供**:
- 初始模板 (本目录)
- 输入输出规范 (0.0.13)
- PMO 7 项合规监督

PMO **不实施** 5 阶段 agent。

## 业务项目职责

业务项目**负责**:
- 从 PMO 模板复制 + 调整
- 实施 5 阶段 agent 代码
- 接入 PMO 监管
- 上报 5 阶段数据

## 关键

- **5 阶段 agent 物理位置在业务项目内** (`eng-roles/`)
- **PMO 给模板, 业务项目实施**
- **必选阶段 (研发/测试/运维) 不可关闭**
- **PMO 7 项合规检查项不可减少**

## 关键决策

- **DEC-2026-0003**: 5 阶段 agent 修正 (2026-06-19)
- **0.0.13**: 5 阶段 agent 输入输出规范
- **PMO 职责**: 给模板 + 定规范 + 监督
- **业务项目职责**: 实施 + 调整 + 上报
