# 业务需求运营 agent 契约模板 (DEC-2026-0003)

**业务项目接入 PMO 实例时必签契约 3: 业务需求运营 agent 契约 (业务自管)**

业务项目 ID: `<biz-project-id>`

**元规则**: 0.0.14 (业务 agent 自定原则)

**关键 (DEC-2026-0003)**:
- 业务需求运营 agent **物理位置在业务项目内** (`biz-projects/<biz_project_id>/biz-agents/`)
- 业务项目**完全自定** (数量/名字/责任/输入输出)
- PMO **不预设不干预** (不固定 8 个)

## 业务 agent 业务项目自定

业务需求运营 agent 的**所有方面**由业务项目自定:

| 维度 | 业务项目自定 |
|---|---|
| 数量 | 业务项目按业务场景配, **不固定 8** |
| 名字 | 业务项目自定 (如: Data-Engineer / Quant-Analyst) |
| 责任 | 业务项目自定 |
| 输入输出 | 业务项目自定 |
| 实现语言/框架 | 业务项目自定 |
| 业务场景 | 业务项目自选 |
| 业务流 | 业务项目自维护 |
| 业务异常 | 业务项目自定义 |
| 业务指标 | 业务项目自维护 |

## PMO 职责 (业务 agent 侧)

PMO **不**:
- 预设业务 agent 数量/名字
- 干预业务 agent 责任/输入输出
- 监督业务 agent 业务逻辑
- 监督业务 agent 业务数据
- 要求业务 agent PMO 7 项合规

PMO **只**:
- 监管业务项目**整体** m2.6 7 项合规
- 监管业务项目 5 阶段 agent (eng-roles/) 0.0.13 合规
- **不**监管业务 agent (biz-agents/) 内容

## 业务项目 biz-agents 契约 (YAML, 业务项目自填)

业务项目接入 PMO 时, **建议**在 `biz-agents/register.yaml` 声明业务 agent 清单:

```yaml
# biz-projects/<biz_project_id>/biz-agents/register.yaml
# 注意: 此文件 PMO 不强制要求, 业务项目自愿
biz_agents:
  biz_project_id: "<biz_project_id>"
  pmo_supervised: false  # 业务 agent PMO 不监管
  agent_count: <N>  # 业务项目自定数量
  
  agents:
    - name: "<Agent-1-Name>"
      file: "<01-agent-1.py>"
      responsibility: "<业务责任 1>"
      business_scenario: "<业务场景 1>"
    
    - name: "<Agent-2-Name>"
      file: "<02-agent-2.py>"
      responsibility: "<业务责任 2>"
      business_scenario: "<业务场景 2>"
    
    # ... 业务项目自定更多业务 agent
```

## 业务 agent 数量建议 (业务项目可调)

| 业务项目规模 | 业务 agent 数量 |
|---|---|
| 简单业务项目 | 2-3 个 |
| 中等业务项目 | 4-6 个 |
| 复杂业务项目 | 7-10 个 |

**关键**: 业务项目**完全自定**, PMO **不强制**。

## 业务项目内 2 类 agent 边界

```
业务项目 (1 个单位)
├── eng-roles/              ← 5 阶段研发 agent (PMO 监管, 0.0.13)
└── biz-agents/             ← 业务需求运营 agent (业务自管, 0.0.14)
```

| 维度 | 5 阶段 agent (PMO 监管) | 业务需求运营 agent (业务自管) |
|---|---|---|
| 物理位置 | eng-roles/ | biz-agents/ |
| 实施 | 业务项目从 PMO 模板复制 + 调整 | 业务项目完全自定 |
| PMO 7 项合规 | **必选** | **不要求** |
| PMO 监督 | **监管** | **不监督** |
| PMO 干预 | 不干预具体实现 | **完全不干预** |
| 元规则 | 0.0.13 | 0.0.14 |

## 业务需求运营 agent 契约签署

业务项目接入 PMO 时, 业务项目必须签本契约 (自愿声明业务 agent 清单), 业务项目代表:
```
业务项目代表: ___________ (签名)
PMO 实例: PMO-Main (Sponsor 授权)
日期: ___________
```

**说明**:
- 本契约**自愿**: 业务项目可签可不签
- PMO **不强制**业务项目声明业务 agent 清单
- 业务项目签了, 只是声明业务 agent 清单给 PMO 备案
- PMO **不监管**业务 agent 内容

## 关键

- **业务需求运营 agent 完全由业务项目自定**
- **PMO 不预设** 业务 agent 数量/名字/责任/输入输出
- **PMO 不干预** 业务 agent 内容
- **业务 agent 不需要 PMO 7 项合规**
- **业务 agent 数量业务项目自定** (不固定 8)

## 关键决策

- **DEC-2026-0003**: 5 阶段 agent 修正 (2026-06-19)
- **0.0.14**: 业务需求运营 agent 自定原则
- **业务 agent vs 5 阶段 agent 边界**: 5 阶段 PMO 监管, 业务 agent 业务自管
