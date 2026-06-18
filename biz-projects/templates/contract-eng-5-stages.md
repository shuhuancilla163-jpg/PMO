# 业务项目内研发 5 阶段契约模板 (DEC-2026-0002)

**业务项目接入 PMO 实例时必签契约 2: 业务项目内研发 5 阶段契约**

业务项目 ID: `<biz-project-id>`

## 研发 5 阶段角色 (PMO 监管, 业务项目可调)

业务项目接入时, 在 `eng-roles/` 声明用了哪些研发角色:

### 1. 需求阶段 (Requirement-Engineer)

```yaml
requirement:
  enabled: true  # 业务项目可关闭 (简化 2 阶段)
  role: "Requirement-Engineer"
  responsibilities:
    - "业务需求调研"
    - "业务需求分析"
    - "业务需求扩展"
  pmo_compliance:
    - "阶段门控 (m1.3)"
    - "决策日志 (m1.1)"
    - "不可变文档 (m0.1)"
  data_source: "requirement/ (业务项目内)"
  pm0_agent: "L2 PMO-Engineer-Agent"
```

### 2. 研发阶段 (Development-Engineer)

```yaml
development:
  enabled: true  # 必选
  role: "Development-Engineer"
  responsibilities:
    - "写代码"
    - "工程实现"
    - "Code Review"
  pmo_compliance:
    - "阶段门控 (m1.3)"
    - "决策日志 (m1.1)"
    - "不可变文档 (m0.1)"
    - "异常拦截 (m0.4)"
  data_source: "development/ (业务项目内)"
  pm0_agent: "L2 PMO-Engineer-Agent"
```

### 3. 测试阶段 (Test-Engineer)

```yaml
test:
  enabled: true  # 必选
  role: "Test-Engineer"
  responsibilities:
    - "单元测试"
    - "集成测试"
    - "验收测试"
  pmo_compliance:
    - "阶段门控 (m1.3)"
    - "异常拦截 (m0.4)"
    - "指标可贯彻 (m1.2)"
  data_source: "test/ (业务项目内)"
  pm0_agent: "L2 PMO-Engineer-Agent"
```

### 4. 运维阶段 (Operations-Engineer)

```yaml
operations:
  enabled: true  # 必选
  role: "Operations-Engineer"
  responsibilities:
    - "部署"
    - "CI/CD"
    - "监控"
    - "灾备"
  pmo_compliance:
    - "阶段门控 (m1.3)"
    - "异常拦截 (m0.4)"
    - "3 层告警 (m0.4)"
    - "灾备 (m0.4)"
  data_source: "operations/ (业务项目内)"
  pm0_agent: "L2 PMO-Engineer-Agent"
```

### 5. 评估阶段 (Evaluation-Engineer)

```yaml
evaluation:
  enabled: true  # 业务项目可关闭
  role: "Evaluation-Engineer"
  responsibilities:
    - "业务评估"
    - "性能评估"
    - "复盘"
  pmo_compliance:
    - "决策日志 (m1.1)"
    - "指标可贯彻 (m1.2)"
    - "Sponsor 报告 (m1.5)"
    - "自进化 (0.0.8)"
  data_source: "evaluation/ (业务项目内)"
  pm0_agent: "L2 PMO-Engineer-Agent"
```

## 业务项目可调整 (但必须符合 PMO)

业务项目接入时, 可:
- **关闭**: 需求阶段, 评估阶段 (业务项目简化)
- **必选**: 研发阶段, 测试阶段, 运维阶段 (业务项目核心)
- **增加**: 业务项目可加自定义阶段 (但必须符合 PMO 7 项)

## 业务项目维度 2 考核 (L2 PMO-Assessor-Agent)

业务项目内研发 5 阶段被 PMO 考核, 考核指标:
- `requirement_phase_compliance` (需求阶段合规)
- `development_phase_compliance` (研发阶段合规)
- `test_phase_compliance` (测试阶段合规)
- `operations_phase_compliance` (运维阶段合规)
- `evaluation_phase_compliance` (评估阶段合规)
- 各阶段决策日志完整度
- 各阶段不可变文档数量
- 各阶段异常拦截率

## 业务项目维度 2 监控 (L2 PMO-Engineer-Agent)

业务项目内研发 5 阶段被 PMO 监控:
- 研发 5 阶段产出 (代码/测试/部署/报告)
- 研发 5 阶段决策日志
- 研发 5 阶段不可变文档
- 研发 5 阶段异常拦截记录
- 研发 5 阶段指标

## 业务项目研发 5 阶段契约生效条件

业务项目研发 5 阶段契约生效:
- 业务项目 eng-roles/ 已声明
- 研发 5 阶段 (或简化 2-3 阶段) 全部符合 PMO 7 项
- 业务项目研发 5 阶段符合 PMO 7 项 (阶段门控/决策日志/不可变文档/异常拦截/指标可贯彻/3 层告警/Sponsor 报告)

## 业务项目研发 5 阶段契约违反处理

| 违反 | 处理 |
|---|---|
| 研发阶段不符合 PMO 7 项 | 警告 + 业务项目整改 |
| 研发阶段未走 PMO 阶段门控 | critical + 业务项目暂停 |
| 研发阶段未记录决策日志 | 警告 + 补录决策日志 |
| 研发阶段不可变文档缺失 | 警告 + 补录不可变文档 |
| 研发阶段异常拦截失败 | critical + 升级到 Sponsor |
| 研发阶段指标未上报 | 警告 + 补报指标 |
| 研发阶段告警失败 | 告警通道修复 + 重新告警 |
| 研发阶段未给 Sponsor 报告 | 警告 + 补 Sponsor 报告 |

## 业务项目研发 5 阶段契约签署

业务项目接入 PMO 时, 业务项目必须签本契约, 业务项目代表:
```
业务项目代表: ___________ (签名)
PMO 实例: PMO-Main (Sponsor 授权)
日期: ___________
```

## 业务项目研发 5 阶段目录结构

```
biz-projects/<biz-project-id>/
├── eng-roles/
│   ├── requirement.yaml
│   ├── development.yaml
│   ├── test.yaml
│   ├── operations.yaml
│   └── evaluation.yaml
├── requirement/    # 需求阶段产出
├── development/    # 研发阶段产出
├── test/           # 测试阶段产出
├── operations/     # 运维阶段产出
└── evaluation/     # 评估阶段产出
```

## 关键决策

- **DEC-2026-0002**: 14 块关键调整 (2026-06-18)
- **5 阶段研发角色**: 需求/研发/测试/运维/评估
- **影响**: m2.3 业务 agent + 研发 agent 设计, 业务项目 eng-roles/ 目录
