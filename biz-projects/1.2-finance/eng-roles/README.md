# 业务项目 1.2-finance eng-roles/

**业务项目 1.2-finance 内部研发 5 阶段 agent** (DEC-2026-0003, 5 阶段 agent 物理位置在业务项目内)

## 5 阶段 agent 清单 (业务项目从 PMO 模板复制 + 业务调整)

| # | 阶段 | 文件 | 必选 | 业务特定调整 |
|---|---|---|---|---|
| 1 | Requirement-Engineer | [01-requirement-engineer.py](./01-requirement-engineer.py) | 否 | + financial_markets / quant_strategy_spec / risk_policy_doc |
| 2 | Development-Engineer | [02-development-engineer.py](./02-development-engineer.py) | **是** | Python + pandas/numpy/zipline/backtrader |
| 3 | Test-Engineer | [03-test-engineer.py](./03-test-engineer.py) | **是** | + historical_market_data / backtest_results (夏普/最大回撤) |
| 4 | Operations-Engineer | [04-operations-engineer.py](./04-operations-engineer.py) | **是** | + market_data_backup (10年合规) / trading_system_sla (99.99%) |
| 5 | Evaluation-Engineer | [05-evaluation-engineer.py](./05-evaluation-engineer.py) | 否 | + strategy_attribution / risk_adjusted_return (sharpe 1.8) |

## 业务项目调整 (基于 PMO 模板)

业务项目 1.2-finance 从 `PMO/templates/eng-roles/` 复制 5 阶段模板, 然后**按业务调整**:
- **保留**: PMO 7 项合规字段 + PMO 规范输入输出字段
- **扩展**: 加业务特定字段 (如: financial_markets / quant_strategy_code / market_data_backup)
- **改名**: 业务项目可改 (本项目保留原名)
- **业务特定工具**: Python + 量化库 (pandas / numpy / zipline / backtrader)

**关键**: PMO 7 项合规检查项**不可减少**, 必选阶段 (研发/测试/运维) **不可关闭**。

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

业务项目 1.2-finance eng-roles/ 注册见 [register.yaml](./register.yaml)

## 关键

- **5 阶段 agent 物理位置在业务项目内** (DEC-2026-0003)
- **PMO 给模板, 业务项目实施 + 业务调整**
- **必选阶段 (研发/测试/运维) 不可关闭**
- **PMO 7 项合规检查项不可减少**
- **业务项目上报 PMO 监督**
