# biz-agents/ — 业务 agent 框架

**空目录, 具体业务 agent 由具体业务项目基于 Sponsor 需求自定**

> 框架态: 这个目录在 `1.x-biz-template` 中是空的。
> 具体业务 agent (如量化/电商/医疗 agent) 在业务项目创建时由 Sponsor 需求驱动定义。

## 框架态说明

| 项目 | 内容 |
|---|---|
| 目录 | `biz-agents/` (空) |
| 用途 | 存放业务 agent 的 Python 文件 |
| 数量 | 具体业务项目自定 |
| 命名 | 具体业务项目自定 |
| PMO 监管 | **不监管** (0.0.14) |

## 业务 agent 框架文件

业务项目创建后, 在 `biz-agents/` 下放入 agent 文件:

```
biz-agents/
├── README.md              # 本文件
├── 01-<agent-name>.py    # 业务 agent 1
├── 02-<agent-name>.py    # 业务 agent 2
└── ...
```

## 业务 agent Python 文件模板

```python
"""
<agent-name>.py — <业务 agent 描述>

具体业务项目: <project-id>
创建时间: <YYYY-MM-DD>
PMO 监管: 无 (0.0.14 业务自管原则)
"""

class <AgentName>Agent:
    """
    业务 agent 基类

    具体业务 agent 由具体业务项目自定:
    - 数量/名字: 具体业务项目自定
    - 职责: 具体业务项目自定
    - 输入输出: 具体业务项目自定
    - 实现语言/框架: 具体业务项目自定
    """

    def __init__(self, biz_project_id: str):
        self.biz_project_id = biz_project_id
        self.name = "<agent-name>"  # 具体业务项目自定
        self.role = "<role>"        # 具体业务项目自定

    def define_inputs(self) -> dict:
        """定义输入"""
        return {}

    def define_outputs(self) -> dict:
        """定义输出"""
        return {}

    def execute(self, context: dict) -> dict:
        """执行业务逻辑"""
        return {"status": "ok"}
```

## 关键原则 (DEC-2026-0003, 0.0.14)

- **PMO 不预设业务 agent 数量/名字/责任/输入输出**
- **PMO 不干预业务 agent 内容**
- **业务 agent 完全由具体业务项目自定**
