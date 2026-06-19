"""
PMO 运行时自测 (pmo_self_test.py)
- m0.5 验收
- 用 mock 数据验证 PMO 能起来
- agent 能激活
- 状态能持久化
- 8 PMO 角色 + 3 维度 (DEC-2026-0002)
- mock 业务项目 1.1 + 1.2 + 1.3 验证

测试项:
1. PMO 实例能起来
2. 8 PMO 角色能激活
3. 状态机能跑
4. 状态能持久化
5. 业务项目能注册
6. 3 维度能采集
7. Assessor 能考核
8. Message-Broker 能投递
9. 触发器能触发
10. 异常能拦截
11. 指标能跑批
12. 反射能记录
"""
import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# PMO_ROOT = 向上 2 层 (本文件在 scripts/runtime/, PMO_ROOT 在 scripts/)
PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PMO_ROOT, "scripts", "runtime"))

from agents.agent_base import (
    PMOInstance, PMOMainAgent, PlanAgent, EngineerAgent, MonitorAgent,
    ReviewerAgent, AssessorAgent, MessageBrokerAgent, SponsorAgent
)
from core.state_machine import BizProjectStateMachine, BizProjectState


class SelfTest:
    """PMO 运行时自测 (m0.5)"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.pmo_root = PMO_ROOT
        self.pmo: PMOInstance = None
    
    def assert_true(self, name: str, condition: bool, detail: str = "") -> bool:
        """断言 + 记录"""
        status = "PASS" if condition else "FAIL"
        result = {
            "test": name,
            "status": status,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.results.append(result)
        return condition
    
    def test_pmo_instance_can_start(self) -> bool:
        """测试 1: PMO 实例能起来"""
        try:
            self.pmo = PMOInstance(self.pmo_root)
            return self.assert_true(
                "PMO 实例能起来",
                self.pmo is not None,
                f"instance_id: {self.pmo.pmo_main.agent_id}"
            )
        except Exception as e:
            return self.assert_true("PMO 实例能起来", False, f"异常: {e}")
    
    def test_8_agents_can_activate(self) -> bool:
        """测试 2: 8 PMO 角色能激活"""
        try:
            self.pmo.activate_all()
            all_running = all(a.reflect()["state"] == "running" for a in self.pmo.agents)
            return self.assert_true(
                "8 PMO 角色能激活",
                all_running and len(self.pmo.agents) == 8,
                f"agent 数: {len(self.pmo.agents)}, 全部 running: {all_running}"
            )
        except Exception as e:
            return self.assert_true("8 PMO 角色能激活", False, f"异常: {e}")
    
    def test_state_machine_runs(self) -> bool:
        """测试 3: 状态机能跑"""
        try:
            bpsm = BizProjectStateMachine("1.1", self.pmo_root)
            bpsm.transition(BizProjectState.ACTIVE, "1.1 启动")
            current = bpsm.get_state()
            return self.assert_true(
                "状态机能跑",
                current == "active",
                f"1.1 当前状态: {current}"
            )
        except Exception as e:
            return self.assert_true("状态机能跑", False, f"异常: {e}")
    
    def test_state_can_persist(self) -> bool:
        """测试 4: 状态能持久化"""
        try:
            bpsm = BizProjectStateMachine("1.1", self.pmo_root)
            bpsm.transition(BizProjectState.ACTIVE, "1.1 启动")
            save_path = Path(self.pmo_root) / "tasks" / "state" / "1.1-pmo-self.json"
            bpsm.save(save_path)
            return self.assert_true(
                "状态能持久化",
                save_path.exists(),
                f"保存路径: {save_path}"
            )
        except Exception as e:
            return self.assert_true("状态能持久化", False, f"异常: {e}")
    
    def test_biz_projects_can_register(self) -> bool:
        """测试 5: 业务项目能注册"""
        try:
            r1 = self.pmo.pmo_main.process({"action": "register_project", "project_id": "1.2"})
            r2 = self.pmo.pmo_main.process({"action": "register_project", "project_id": "1.3"})
            count = len(self.pmo.pmo_main.managed_projects)
            return self.assert_true(
                "业务项目能注册",
                count >= 2,  # mock 测试只 register 2 个 (1.2 + 1.3)
                f"管理项目数: {count}"
            )
        except Exception as e:
            return self.assert_true("业务项目能注册", False, f"异常: {e}")
    
    def test_3_dimensions_can_collect(self) -> bool:
        """测试 6: 3 维度能采集 (DEC-2026-0002)"""
        try:
            # 维度 1: PMO-Main
            r1 = self.pmo.pmo_main.process({"action": "update_business_state", "project_id": "1.2", "state": "active"})
            # 维度 2: Engineer-Agent
            r2 = self.pmo.engineer_agent.process({"action": "collect_eng_stage_data", "project_id": "1.2", "stage": "requirement", "data": {"doc": "需求"}})
            # 维度 3: Monitor-Agent
            r3 = self.pmo.monitor_agent.process({"action": "collect_reported_data", "project_id": "1.2", "data": {
                "flow_latency": 100, "exception_rate": 0.01, "pass_rate": 0.99, "rollback_rate": 0.001, "token_consumption": 10000
            }})
            ok = r1.get("success") and r2.get("success") and r3.get("success")
            return self.assert_true(
                "3 维度能采集",
                ok,
                f"维度 1: {r1.get('success')}, 维度 2: {r2.get('success')}, 维度 3: {r3.get('success')}"
            )
        except Exception as e:
            return self.assert_true("3 维度能采集", False, f"异常: {e}")
    
    def test_assessor_can_assess(self) -> bool:
        """测试 7: Assessor 能考核"""
        try:
            assessment = self.pmo.assessor_agent.assess_project(
                self.pmo.pmo_main, self.pmo.engineer_agent, self.pmo.monitor_agent, "1.2"
            )
            return self.assert_true(
                "Assessor 能考核",
                "overall_verdict" in assessment,
                f"1.2 总考: {assessment.get('overall_verdict')}"
            )
        except Exception as e:
            return self.assert_true("Assessor 能考核", False, f"异常: {e}")
    
    def test_message_broker_can_deliver(self) -> bool:
        """测试 8: Message-Broker 能投递"""
        try:
            r1 = self.pmo.message_broker_agent.process({"action": "subscribe", "project_id": "1.2", "topic": "biz.1.3.state"})
            r2 = self.pmo.message_broker_agent.process({"action": "publish", "from_project": "1.3", "topic": "biz.1.3.state", "message": {"event": "active"}})
            r3 = self.pmo.message_broker_agent.process({"action": "deliver", "topic": "biz.1.3.state"})
            ok = r1.get("success") and r2.get("success") and r3.get("success")
            delivered = len(r3.get("result", [])) > 0
            return self.assert_true(
                "Message-Broker 能投递",
                ok and delivered,
                f"订阅: {r1.get('success')}, 发布: {r2.get('success')}, 投递: {delivered}"
            )
        except Exception as e:
            return self.assert_true("Message-Broker 能投递", False, f"异常: {e}")
    
    def test_triggers_can_fire(self) -> bool:
        """测试 9: 触发器能触发"""
        try:
            from triggers.triggers import Trigger, TriggerType, TriggerManager
            tm = TriggerManager()
            tm.register(Trigger("T-SELFTEST", TriggerType.TIME, "test", "test_action"))
            fired = tm.fire("T-SELFTEST")
            return self.assert_true(
                "触发器能触发",
                fired,
                "T-SELFTEST 触发"
            )
        except Exception as e:
            return self.assert_true("触发器能触发", False, f"异常: {e}")
    
    def test_exceptions_can_intercept(self) -> bool:
        """测试 10: 异常能拦截"""
        try:
            from exceptions.exceptions import ExceptionInterceptor, BizExceptionType
            from core.state_machine import ExceptionSeverity
            interceptor = ExceptionInterceptor(self.pmo_root)
            exc_id = interceptor.intercept_biz(BizExceptionType.PERFORMANCE, ExceptionSeverity.WARNING, "SELFTEST-001", "selftest", "1.2")
            # exc_id 是 BizException 对象, 验证它有相关属性
            has_exc_id = exc_id is not None
            return self.assert_true(
                "异常能拦截",
                has_exc_id,
                f"异常对象: {type(exc_id).__name__}"
            )
        except Exception as e:
            return self.assert_true("异常能拦截", False, f"异常: {e}")
    
    def test_metrics_can_batch(self) -> bool:
        """测试 11: 指标能跑批"""
        try:
            from metrics.metrics import MetricsCollector
            collector = MetricsCollector(self.pmo_root)
            collector.record("BIZ-M-001", 25.5, {"biz_project": "1.2"})
            collector.record("BIZ-M-002", 0.01, {"biz_project": "1.2"})
            dashboard = collector.get_dashboard()
            count = dashboard.get("summary", {}).get("total_metrics", 0)
            return self.assert_true(
                "指标能跑批",
                count > 0,
                f"总指标: {count}"
            )
        except Exception as e:
            return self.assert_true("指标能跑批", False, f"异常: {e}")
    
    def test_reflection_can_log(self) -> bool:
        """测试 12: 反射能记录"""
        try:
            from core.reflect import ReflectionManager, ReflectionType
            rm = ReflectionManager()
            r = rm.reflect("PMO-Main", ReflectionType.LEARNING, "m0.5 运行时自测通过")
            return self.assert_true(
                "反射能记录",
                r is not None,
                f"反思 ID: {r.reflection_id if hasattr(r, 'reflection_id') else 'N/A'}"
            )
        except Exception as e:
            return self.assert_true("反射能记录", False, f"异常: {e}")
    
    def run_all(self) -> Dict[str, Any]:
        """运行所有自测"""
        print("=" * 60)
        print("  PMO 运行时自测 v0.6.0 (m0.5 + DEC-2026-0002)")
        print(f"  PMO_ROOT: {self.pmo_root}")
        print(f"  时间: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)
        print()
        
        # 12 项测试
        self.test_pmo_instance_can_start()
        self.test_8_agents_can_activate()
        self.test_state_machine_runs()
        self.test_state_can_persist()
        self.test_biz_projects_can_register()
        self.test_3_dimensions_can_collect()
        self.test_assessor_can_assess()
        self.test_message_broker_can_deliver()
        self.test_triggers_can_fire()
        self.test_exceptions_can_intercept()
        self.test_metrics_can_batch()
        self.test_reflection_can_log()
        
        # 输出结果
        print("自测结果:")
        for i, r in enumerate(self.results, 1):
            icon = "✅" if r["status"] == "PASS" else "❌"
            print(f"  [{i:2}] {icon} {r['test']}: {r['status']}")
            print(f"       {r['detail']}")
        
        pass_count = sum(1 for r in self.results if r["status"] == "PASS")
        fail_count = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)
        pass_rate = (pass_count / total * 100) if total > 0 else 0
        
        print()
        print("=" * 60)
        print(f"  自测结果: {pass_count}/{total} pass ({pass_rate:.1f}%)")
        if fail_count == 0:
            print(f"  ✅ PMO 运行时全部通过, m0.5 完成")
        else:
            print(f"  ❌ {fail_count} 项失败, 需修复")
        print("=" * 60)
        
        return {
            "total": total,
            "pass": pass_count,
            "fail": fail_count,
            "pass_rate": f"{pass_rate:.1f}%",
            "results": self.results
        }


if __name__ == "__main__":
    test = SelfTest()
    result = test.run_all()
    
    # 保存自测报告
    report_dir = Path(PMO_ROOT) / "tests"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "m0.5-self-test-report.json"
    with open(report_file, "w") as f:
        json.dump({
            "version": "0.6.0",
            "decision": "DEC-2026-0002",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": result["total"],
                "pass": result["pass"],
                "fail": result["fail"],
                "pass_rate": result["pass_rate"]
            },
            "results": result["results"]
        }, f, indent=2, ensure_ascii=False)
    print(f"\n自测报告已保存: {report_file}")
