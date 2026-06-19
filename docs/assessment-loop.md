# PMO 考核闭环 (DEC-2026-0009, m0.9)

**考核闭环**：PMO 持续考核业务项目，确保其符合规范。

---

## 1. 考核架构

```
业务项目
    │  指标上报（每小时）
    ▼
metrics/ ← MetricsCollector
    │
    ▼
ThresholdEngine  ← 加载 config/thresholds.yaml
    │
    ├──→ 3 维度加权得分
    ├──→ 考核报告（reports/assessments/<id>/）
    │
    ▼
OperationsMonitor  ← 违规告警
    │
    ▼
Sponsor  ← 重大违规通知
```

---

## 2. 考核维度

### 维度 1: 业务项目整体（权重 30%）

| 指标 | warn | critical | 方向 |
|---|---|---|---|
| decision_log_completeness | 0.80 | 0.60 | higher |
| archive_completeness | 0.85 | 0.70 | higher |
| state_legality_rate | 0.90 | 0.70 | higher |
| quota_usage_rate | 0.80 | 1.00 | lower |

### 维度 2: 业务项目内研发 5 阶段（权重 30%）

| 指标 | warn | critical | 方向 |
|---|---|---|---|
| deploy_success_rate | 0.95 | 0.90 | higher |
| exception_interception_rate | 0.90 | 0.80 | higher |
| performance_baseline_rate | 0.85 | 0.70 | higher |
| availability | 0.99 | 0.95 | higher |

### 维度 3: 业务上报合规（权重 40%）

| 指标 | warn | critical | 方向 |
|---|---|---|---|
| flow_latency（秒） | 200 | 300 | lower |
| exception_rate | 0.05 | 0.20 | lower |
| pass_rate | 0.90 | 0.80 | higher |
| rollback_rate | 0.02 | 0.05 | lower |
| token_consumption | 5000 | 8000 | lower |

---

## 3. 判定规则

### 单指标判定

| 方向 | ok | warning | critical |
|---|---|---|---|
| lower_is_better | value < warn | warn ≤ value < critical | value ≥ critical |
| higher_is_better | value > warn | critical ≤ value ≤ warn | value ≤ critical |

### 维度判定（维度得分）

| 得分 | 判定 |
|---|---|
| ≥ 80 | compliant（合规） |
| 60–80 | warning（警告） |
| < 60 | violation（违规） |

### 整体判定（加权平均）

| 得分 | 判定 |
|---|---|
| ≥ 90 | excellent（优秀） |
| 75–90 | good（良好） |
| 60–75 | warning（警告） |
| < 60 | violation（违规） |

### 维度得分计算

得分 = Σ(单指标得分 × 权重) / Σ权重

单指标得分：ok=100 / warning=60 / critical=20 / no_data=0

---

## 4. 考核触发机制

| 触发方式 | 频率 | 说明 |
|---|---|---|
| 定时跑批 | 每 6 小时 | `ThresholdEngine.run_periodic_assessment()` |
| 即时检查 | 实时 | `ThresholdEngine.check_thresholds()` |
| 业务项目上报时 | 实时 | 上报指标后自动触发比对 |
| PMO 自测 | 按需 | `m0_9_self_test.py` |

---

## 5. 报告输出

- 路径：`reports/assessments/<project_id>/<timestamp>.json`
- 最新报告：`reports/assessments/<project_id>/latest.json`
- 汇总报告：`reports/assessments/latest-summary.json`

报告字段：

```json
{
  "report_id": "ASSESS-20260619-001",
  "project_id": "1.2-finance",
  "timestamp": "2026-06-19T12:00:00Z",
  "overall_score": 82.5,
  "overall_verdict": "good",
  "dimension_1": { "score": 80.0, "verdict": "compliant", "violations": [] },
  "dimension_2": { "score": 85.0, "verdict": "compliant", "violations": [] },
  "dimension_3": { "score": 82.5, "verdict": "compliant", "violations": [] },
  "violations": [],
  "violation_count": 0
}
```

---

## 6. 阈值覆盖

业务项目可通过 `biz-projects/<id>/reports/thresholds.yaml` 覆盖 PMO 默认阈值。

覆盖优先级：`项目级 thresholds.yaml > config/thresholds.yaml`

---

## 7. 相关文件

| 文件 | 位置 | 用途 |
|---|---|---|
| thresholds.yaml | config/ | PMO 默认阈值配置 |
| threshold_engine.py | scripts/runtime/assessment/ | 考核引擎 |
| onboarding_syncer.py | scripts/runtime/norm_sync/ | 接入时全量同步 |
| norm_pusher.py | scripts/runtime/norm_sync/ | 运行时增量同步 |
| m0_9_self_test.py | scripts/runtime/norm_sync/ | 自测 8 项 |
| biz-project-onboarding-5-steps.md | docs/ | 业务项目接入流程 |

---

## 8. 关键决策

- **DEC-2026-0009**: m0.9 PMO 规范同步 + 考核闭环（2026-06-19）
- 阈值定义 + 考核引擎 + 运行时同步 + 自测
- 影响：m2.6 业务项目管理流程更新，接入文档更新
