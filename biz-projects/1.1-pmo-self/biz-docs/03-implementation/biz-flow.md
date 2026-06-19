# 业务流编排

**业务项目**: 1.1-pmo-self
**版本**: v1.0.0
**阶段**: development
**Git Commit**: 业务流 v1.0.0 (biz.1.1-pmo-self.v1.0.0-rc.2)

## PMO 自建迭代流

1. Sponsor 下发 PMO 任务 (如: 新增元规则)
2. PMO-Main 注册任务
3. Plan-Agent 制定计划 (m1.3 核心执行)
4. Engineer-Agent 实施 (Git commit)
5. Monitor-Agent 监控 (3 维度)
6. Assessor-Agent 考核
7. Reviewer-Agent 审计
8. PMO-Main 出报告

## 版本发布流

1. Engineer-Agent 完成功能实施
2. Reviewer-Agent 审计
3. Assessor-Agent 考核通过
4. PMO-Main 打 Git tag (biz.1.1-pmo-self.vX.Y.Z)
5. Monitor-Agent 记录版本到 PMO config
