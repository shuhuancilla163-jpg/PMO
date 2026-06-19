# 业务设计文档

**业务项目**: 1.1-pmo-self
**版本**: v1.0.0
**阶段**: development
**Git Commit**: 设计文档 v1.0.0 (biz.1.1-pmo-self.v1.0.0-rc.2)

## 1. PMO 自建架构

```
Sponsor (L0)
    ↓ 发起任务 / 审批决策
PMO-Main (L1)
    ├── Plan-Agent (制定计划)
    ├── Engineer-Agent (实施)
    ├── Monitor-Agent (监控 3 维度)
    ├── Assessor-Agent (考核)
    ├── Reviewer-Agent (审计)
    └── Message-Broker-Agent (消息路由)
```

## 2. 3 维度监控

| 维度 | 监控内容 | 数据来源 |
|---|---|---|
| 维度 1 | 业务项目整体健康 | biz-projects/*/register.yaml |
| 维度 2 | 5 阶段研发合规 | biz-projects/*/eng-roles/reports/*.yaml |
| 维度 3 | 业务性能报告合规 | biz-projects/*/reports/*.yaml |

## 3. 版本管理

- Git tag 格式: `biz.1.1-pmo-self.v<MAJOR>.<MINOR>.<PATCH>`
- 版本号规则遵循 semver
- 每次发布需完整 biz-docs 文档
