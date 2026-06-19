# 1.x-examples/quant-finance/ — 量化金融参考示例

**仅供参考的业务示例, 不是 PMO 框架的一部分**

> **框架态原则**: PMO 框架不管具体业务 domain。具体业务 domain (如量化金融) 由 Sponsor 后续注入。
> 这个目录是历史参考, 展示了具体业务 agent 长什么样 —— 但业务项目接入 PMO 时应该自己定义。

## 目录内容

```
1.x-examples/quant-finance/
└── biz-agents/       # 参考示例: 量化金融业务 agent (仅供参考)
    ├── 01-data-engineer.py
    ├── 02-quant-analyst.py
    ├── 03-risk-manager.py
    ├── 04-portfolio-mgr.py
    ├── 05-compliance-officer.py
    └── 06-reporting-analyst.py
```

## 这个目录的特点

- **是参考示例, 不是模板**
- 具体业务 agent 的实现 (Data-Engineer / Quant-Analyst / Risk-Manager 等)
- 基于具体业务场景 (量化金融)
- 展示了业务 agent 的 Python 代码格式

## 正确使用方式

当 Sponsor 定义了具体业务需求 (如"我要做一个量化交易系统"), AI Operator 基于 `1.x-biz-template` 创建新的业务项目, 然后:
- 决定需要哪些业务 agent (可能与这里的不同)
- 定义 agent 的具体职责
- 写入 E1/E2/E3 (m2.1)
- 产出 biz-docs (m2.2)

## 框架态 vs 实现态

| 层级 | 状态 | 内容 |
|---|---|---|
| PMO 框架 (m0/m1) | 框架态 | 治理规范, 不变 |
| 业务项目骨架 (1.x-biz-template) | 框架态 | 空模板, 待填充 |
| 具体业务项目 | **实现态** | Sponsor 注入业务需求后定义 |
| 参考示例 (1.x-examples) | **历史实现态** | 已移入参考, 非框架 |
