# 发布说明

**业务项目**: 1.1-pmo-self
**Git tag**: biz.1.1-pmo-self.v1.0.0
**发布日期**: 2026-06-19

---

## v1.0.0 — 初始发布 (2026-06-19)

### 概述

PMO 自建系统 v1.0.0 初始发布, 完成 PMO 治理框架的基础建设。

### 新增

- **17 项 PMO 元规则**: 0.0.1 ~ 0.0.17
- **8 个 PMO 角色**: PMO-Main / Plan-Agent / Engineer-Agent / Monitor-Agent / Assessor-Agent / Reviewer-Agent / Message-Broker-Agent / Logger-Agent
- **3 维度监控**: 整体健康 / 5 阶段研发合规 / 性能报告合规
- **完整 biz-docs 文档**: 需求/设计/实施/发布 4 类文档

### 业务不可变文档清单

| 文档 | 版本 | Git Commit |
|---|---|---|
| biz-requirements.md | v1.0.0 | biz.1.1-pmo-self.v1.0.0-rc.1 |
| biz-design.md | v1.0.0 | biz.1.1-pmo-self.v1.0.0-rc.2 |
| biz-flow.md | v1.0.0 | biz.1.1-pmo-self.v1.0.0-rc.2 |
| release-notes.md | v1.0.0 | biz.1.1-pmo-self.v1.0.0 |

### PMO 元数据

- E1: register.yaml v1.0.0 ✅
- E2: data-schema.yaml v1.0.0 ✅
- E3: glossary.yaml v1.0.0 ✅
- eng-roles/: 5 阶段研发 agent ✅
- biz-docs/: 业务不可变文档 ✅ (m2.2)
