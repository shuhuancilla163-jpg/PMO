# biz-docs/ — 业务不可变文档 (F1, m2.2, DEC-2026-0006)

**业务项目的业务产出文档, 基于 E1/E2/E3 (m2.1)**

---

## 01-requirements/ — 需求阶段

### biz-requirements.md

```markdown
# 业务需求文档 (biz-requirements.md)

**业务项目**: 1.1-pmo-self (PMO 系统自建)
**版本**: v1.0.0
**阶段**: P1-spec
**基于**: data-schema.yaml (E2) + glossary.yaml (E3)

## 1. 业务需求

### 1.1 核心业务实体 (基于 E2 data-schema)

- **task**: PMO 任务
- **decision**: PMO 决策
- **metric**: PMO 指标

### 1.2 业务术语 (基于 E3 glossary)

- task = 任务
- decision = 决策
- phase = PMO 阶段
- metric = PMO 指标
- compliance = 合规
```

---

## 02-design/ — 设计阶段

### biz-design.md

```markdown
# 业务设计文档 (biz-design.md)

**业务项目**: 1.1-pmo-self
**版本**: v1.0.0
**阶段**: P2-impl

## 1. PMO 自建业务流

- Sponsor 发起任务
- PMO-Main 分配
- Plan-Agent 制定计划
- Engineer-Agent 实施
- Monitor-Agent 监控
- Assessor-Agent 考核
- Reviewer-Agent 审计
```

---

## 03-implementation/ — 实施阶段

### biz-flow.md

```markdown
# 业务流编排 (biz-flow.md, m2.4 前身)

**业务项目**: 1.1-pmo-self
**版本**: v1.0.0

## PMO 自建流

1. Sponsor 下发任务
2. PMO-Main 注册任务
3. Plan-Agent 制定计划
4. Engineer-Agent 实施
5. Monitor-Agent 监控
6. Assessor-Agent 考核
```

---

## 04-release/ — 发布阶段

### release-notes.md

```markdown
# 发布说明 (release-notes.md)

**业务项目**: 1.1-pmo-self
**版本**: v1.0.0
**发布日期**: 2026-06-19

## v1.0.0 — 初始发布

### 新增

- PMO 自建业务流
- 3 个业务实体 (task/decision/metric)
- 7 个业务术语
- 5 个业务 agent role

### PMO 版本

- Git tag: biz.1.1-pmo-self.v1.0.0
```
