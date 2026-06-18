"""
PMO 运行时入口 (pmo_runtime.py)
- 统一入口, 启动 PMO 实例
- 演示完整流程: 存储 → 运行时 → 部署 → 运维 → 自测
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# 导入所有运行时模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.state_machine import (
    PhaseGate, BizProjectState, TaskState, AgentState,
    ExceptionLayer, ExceptionSeverity,
    StateMachine, BizProjectStateMachine
)
from core.reflect import ReflectionManager, ReflectionType
from agents.agent_base import (
    PMOAgent, PMOMainAgent, PlanAgent, EngineerAgent, ReviewerAgent, SponsorAgent,
    PMOInstance
)
from triggers.triggers import Trigger, TriggerType, TriggerManager
from exceptions.exceptions import (
    BizExceptionType, BizException, PMOInstanceException,
    PMOException, ExceptionInterceptor
)
from protocol.protocol import Protocol, Message, MessageType
from notify.notify import SponsorNotifier, NotifyChannel
from metrics.metrics import MetricsCollector, MetricCategory


def main():
    """PMO 运行时主入口"""
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("  PMO 运行时 v0.2.0 — 完整演示")
    print(f"  PMO_ROOT: {PMO_ROOT}")
    print(f"  时间: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    print()
    
    # ============================================
    # 阶段 1: 存储层 (m0.1 已完成)
    # ============================================
    print("【阶段 1: 存储层 m0.1】")
    print(f"  - Git 仓库: ✅ (c1cf5a4 + v0.1.0)")
    print(f"  - 不可变文档库: ✅ (0.0.1~0.0.10)")
    print(f"  - 业务知识库 2 层: ✅ (general + specific)")
    print(f"  - 指标库: ✅ (业务/治理/工程 3 类)")
    print(f"  - 1.1 PMO 自建: ✅ (已注册)")
    print()
    
    # ============================================
    # 阶段 2: 运行时 (m0.2)
    # ============================================
    print("【阶段 2: 运行时 m0.2】")
    
    # 1. 状态机
    print("\n[1] 状态机")
    bpsm = BizProjectStateMachine("1.1", PMO_ROOT)
    bpsm.transition(BizProjectState.ACTIVE, "1.1 启动")
    bpsm.save(Path(PMO_ROOT) / "tasks" / "state" / "1.1-pmo-self.json")
    print(f"  - 1.1 业务项目状态机: {bpsm.get_state()}")
    
    # 2. PMO 实例 (5 agent)
    print("\n[2] PMO 实例 (1 个, 管 5 agent, 三权分立)")
    pmo = PMOInstance(PMO_ROOT)
    pmo.activate_all()
    for agent in pmo.agents:
        print(f"  - {agent.layer} {agent.name}: {agent.reflect()['state']}")
    
    # 3. 触发器
    print("\n[3] 触发器 (4 类: 时间/事件/状态/手动)")
    tm = TriggerManager()
    tm.register(Trigger("T-001", TriggerType.TIME, "cron: 0 9 * * *", "run_daily_metrics"))
    tm.register(Trigger("T-002", TriggerType.EVENT, "exception > 0.2", "notify_pmo"))
    tm.register(Trigger("T-003", TriggerType.STATE, "active", "start_monitoring"))
    tm.register(Trigger("T-004", TriggerType.MANUAL, "sponsor", "sponsor_review"))
    for t in tm.list_triggers():
        print(f"  - {t['trigger_id']}: {t['trigger_type']}")
    
    # 4. 3 层异常拦截
    print("\n[4] 3 层异常拦截 (0.0.10)")
    interceptor = ExceptionInterceptor(PMO_ROOT)
    interceptor.pmo_spec_audit()  # L0 规范, 不参与业务
    interceptor.intercept_biz(BizExceptionType.PERFORMANCE, ExceptionSeverity.CRITICAL, "B004", "流耗时>300s", "1.1")
    interceptor.intercept_pmo(ExceptionSeverity.CRITICAL, "P002", "1.1 异常率>20%")
    
    # 5. 通信协议
    print("\n[5] 通信协议")
    proto = Protocol()
    proto.notification("PMO-Main", "Plan-Agent", {"action": "audit"}, "L1→L2")
    proto.escalation("PMO-Main", "Sponsor", {"severity": "critical"}, "L1→L0")
    print(f"  - 消息数: {len(proto.get_messages())}")
    
    # 6. Sponsor 通知
    print("\n[6] Sponsor 通知 (3 层)")
    notifier = SponsorNotifier(PMO_ROOT)
    notifier.notify_brief("m0.2 运行时完成", {"phase": "M0.2", "complexity": 5})
    notifier.notify_dashboard("指标看板", {"business_5": 5, "governance_8": 8, "engineering_8": 8})
    notifier.notify_instant("重大异常", {"code": "P002"}, "critical")
    print(f"  - Sponsor 收件箱: {len(notifier.get_sponsor_inbox())} 条")
    
    # 7. 指标跑批
    print("\n[7] 指标跑批 (业务 5 + 治理 8 + 工程 8 = 21 项)")
    collector = MetricsCollector(PMO_ROOT)
    collector.record("BIZ-M-001", 25.5, {"biz_project": "1.1"})
    collector.record("BIZ-M-002", 0.0, {"biz_project": "1.1"})
    collector.record("BIZ-M-003", 100.0, {"biz_project": "1.1"})
    collector.record("BIZ-M-004", 0.0, {"biz_project": "1.1"})
    collector.record("BIZ-M-005", 2500, {"biz_project": "1.1"})
    collector.record("GOV-M-001", 100.0, {})
    collector.record("GOV-M-002", 100.0, {})
    collector.record("GOV-M-003", 100.0, {})
    dashboard = collector.get_dashboard()
    print(f"  - 总指标: {dashboard['summary']['total_metrics']} 项")
    print(f"  - 业务: {dashboard['summary']['by_category']['business']}, 治理: {dashboard['summary']['by_category']['governance']}, 工程: {dashboard['summary']['by_category']['engineering']}")
    
    # 8. 反射
    print("\n[8] 反射 (0.0.8 自进化)")
    rm = ReflectionManager()
    r = rm.reflect("PMO-Main", ReflectionType.LEARNING, "m0.2 运行时 8 个子模块全部完成")
    print(f"  - 反思: {r.reflection_id}")
    
    # ============================================
    # 阶段 3-5: 待 m0.3/m0.4/m0.5
    # ============================================
    print("\n【阶段 3-5: 待 m0.3/m0.4/m0.5】")
    print("  - m0.3 部署环境: pending")
    print("  - m0.4 运维: pending")
    print("  - m0.5 运行时自测: pending")
    
    # ============================================
    # 状态报告
    # ============================================
    print("\n" + "=" * 60)
    print("  m0.2 运行时状态")
    print("=" * 60)
    status = pmo.get_status()
    print(f"  - PMO 实例: {status['instance_id']}")
    print(f"  - agent 总数: {status['agent_count']}")
    print(f"  - 管理项目: {status['managed_projects']}")
    print(f"  - 三权分立: L0={status['three_powers']['L0_sponsor']}, L1={status['three_powers']['L1_pmo_main']}, L2={status['three_powers']['L2_judicial']}")
    print(f"  - 异常拦截: L1={interceptor.intercepted_count[ExceptionLayer.PMO_INSTANCE]}, L2={interceptor.intercepted_count[ExceptionLayer.BIZ_PROJECT]}")
    print(f"  - 触发器: {len(tm.list_triggers())} 个")
    print(f"  - 消息: {len(proto.get_messages())} 条")
    print(f"  - Sponsor 通知: {len(notifier.get_sponsor_inbox())} 条")
    print(f"  - 指标: {dashboard['summary']['total_metrics']} 项")
    print(f"  - 反思: {rm.get_statistics()['total_reflections']} 条")
    print()
    print("✅ m0.2 运行时完成, v0.2.0")


if __name__ == "__main__":
    main()
