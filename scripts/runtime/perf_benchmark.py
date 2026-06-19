"""
PMO 性能基线 (perf_benchmark.py)
- 启动时间
- 内存使用
- CPU 使用
- 业务流耗时 (mock)
- 指标跑批耗时
- 异常拦截耗时
- 通信协议耗时
- 3 维度采集耗时 (DEC-2026-0002)
- 3 维度考核耗时 (DEC-2026-0002)
- 项目间消息耗时 (DEC-2026-0002)

输出: 性能基线报告, 用于 m0.4 运维监控的 baseline
DEC-2026-0002: 8 PMO 角色 + 3 维度分离
"""
import os
import sys
import time
import json
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil 未安装, 性能基线将跳过内存/CPU 监控")
import resource
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent_base import PMOInstance
from core.state_machine import BizProjectStateMachine, BizProjectState
from triggers.triggers import Trigger, TriggerType, TriggerManager
from exceptions.exceptions import ExceptionInterceptor, BizExceptionType
from protocol.protocol import Protocol
from notify.notify import SponsorNotifier
from metrics.metrics import MetricsCollector
from core.state_machine import ExceptionSeverity


def get_memory_mb():
    """获取当前进程内存 (MB)"""
    if not HAS_PSUTIL:
        # 用 resource.getrusage 估算
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return usage.ru_maxrss / 1024  # KB -> MB (macOS)
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def get_cpu_percent():
    """获取当前进程 CPU 使用率"""
    if not HAS_PSUTIL:
        return 0.0
    process = psutil.Process()
    return process.cpu_percent(interval=0.1)


def benchmark(name: str, func, *args, **kwargs):
    """基准测试包装器"""
    start_time = time.time()
    start_mem = get_memory_mb()
    start_cpu = get_cpu_percent()
    
    result = func(*args, **kwargs)
    
    end_time = time.time()
    end_mem = get_memory_mb()
    end_cpu = get_cpu_percent()
    
    return {
        "name": name,
        "duration_ms": (end_time - start_time) * 1000,
        "memory_delta_mb": end_mem - start_mem,
        "memory_total_mb": end_mem,
        "cpu_delta_pct": end_cpu - start_cpu,
        "result": result
    }


def main():
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("  PMO 性能基线 v0.3.0 (DEC-2026-0002, 8 PMO 角色 + 3 维度)")
    print(f"  PMO_ROOT: {PMO_ROOT}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  psutil: {psutil.__version__ if HAS_PSUTIL else '未安装 (跳过内存/CPU 监控)'}")
    print(f"  时间: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    print()
    
    results = []
    
    # 1. 启动 PMO 实例
    print("[1] PMO 实例启动 (8 PMO 角色)")
    r = benchmark("PMO 实例启动", lambda: PMOInstance(PMO_ROOT))
    results.append(r)
    pmo = r["result"]
    print(f"  - 耗时: {r['duration_ms']:.1f}ms")
    print(f"  - 内存: {r['memory_total_mb']:.1f}MB")
    print(f"  - agent 数: 8 (3 维度分离)\n")
    
    # 2. 激活 8 个 agent
    print("[2] 8 agent 激活 (16 次状态转换: idle→activated→running)")
    def activate_all():
        pmo.activate_all()
        return pmo
    
    r = benchmark("8 agent 激活", activate_all)
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (8 agent 平均 {r['duration_ms']/8:.1f}ms)")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # 2.5 维度 1 业务项目注册 (PMO-Main)
    print("[2.5] 维度 1 业务项目注册 (PMO-Main)")
    r = benchmark("维度 1 业务项目注册", lambda: [
        pmo.pmo_main.process({"action": "register_project", "project_id": f"1.{i}"}) for i in range(1, 11)
    ])
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (10 业务项目注册, 平均 {r['duration_ms']/10:.2f}ms/项目)\n")
    
    # 2.6 维度 2 研发 5 阶段数据采集 (Engineer-Agent)
    print("[2.6] 维度 2 研发 5 阶段数据采集 (Engineer-Agent)")
    r = benchmark("维度 2 研发 5 阶段采集", lambda: [
        pmo.engineer_agent.process({"action": "collect_eng_stage_data", "project_id": "1.1", "stage": stage, "data": {}})
        for stage in pmo.engineer_agent.ENG_5_STAGES for _ in range(10)
    ])
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (50 阶段数据采集, 平均 {r['duration_ms']/50:.2f}ms/采集)\n")
    
    # 2.7 维度 3 业务项目上报 (Monitor-Agent)
    print("[2.7] 维度 3 业务项目上报 (Monitor-Agent)")
    r = benchmark("维度 3 业务项目上报", lambda: [
        pmo.monitor_agent.process({"action": "collect_reported_data", "project_id": "1.1", "data": {
            "flow_latency": 100, "exception_rate": 0.01, "pass_rate": 0.99, "rollback_rate": 0.001, "token_consumption": 10000
        }}) for _ in range(50)
    ])
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (50 上报, 平均 {r['duration_ms']/50:.2f}ms/上报)\n")
    
    # 2.8 Assessor 3 维度考核
    print("[2.8] Assessor 3 维度考核")
    r = benchmark("Assessor 3 维度考核", lambda: [
        pmo.assessor_agent.assess_project(pmo.pmo_main, pmo.engineer_agent, pmo.monitor_agent, "1.1") for _ in range(10)
    ])
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (10 考核, 平均 {r['duration_ms']/10:.2f}ms/考核)\n")
    
    # 2.9 Message-Broker 项目间消息
    print("[2.9] Message-Broker 项目间消息 (经 PMO 中介)")
    r = benchmark("项目间消息 100 条", lambda: [
        pmo.message_broker_agent.process({"action": "publish", "from_project": "1.1", "topic": f"biz.1.{i}.state", "message": {"i": i}}) for i in range(100)
    ])
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (100 消息, 平均 {r['duration_ms']/100:.2f}ms/消息)\n")
    
    # 3. 业务项目状态机 (10 次转换)
    print("[3] 业务项目状态机 (10 次转换)")
    def state_transitions():
        bpsm = BizProjectStateMachine("1.1", PMO_ROOT)
        bpsm.transition(BizProjectState.ACTIVE, "start")
        bpsm.transition(BizProjectState.PAUSED, "pause")
        bpsm.transition(BizProjectState.ACTIVE, "resume")
        bpsm.transition(BizProjectState.COMPLETED, "complete")
        return bpsm
    
    r = benchmark("状态机 10 次转换", state_transitions)
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # 4. 触发器 (10 个 + 10 次触发)
    print("[4] 触发器 (10 个 + 10 次触发)")
    def trigger_ops():
        tm = TriggerManager()
        for i in range(10):
            tm.register(Trigger(f"T-{i:03d}", TriggerType.TIME, "test", "test_action"))
        for i in range(10):
            tm.fire(f"T-{i:03d}")
        return tm
    
    r = benchmark("触发器 10 个 + 10 次触发", trigger_ops)
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (10 个触发器 + 10 次触发)")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # 5. 异常拦截 (3 层, 100 次)
    print("[5] 异常拦截 3 层 (100 次)")
    def exception_ops():
        interceptor = ExceptionInterceptor(PMO_ROOT)
        for i in range(100):
            interceptor.intercept_biz(BizExceptionType.PERFORMANCE, ExceptionSeverity.WARNING, f"B{i:03d}", f"test {i}")
        return interceptor
    
    r = benchmark("异常拦截 100 次", exception_ops)
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (平均 {r['duration_ms']/100:.2f}ms/次)")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # 6. 通信协议 (100 条消息)
    print("[6] 通信协议 (100 条消息)")
    def protocol_ops():
        proto = Protocol()
        for i in range(100):
            proto.notification("PMO-Main", "Plan-Agent", {"i": i})
        return proto
    
    r = benchmark("通信 100 条", protocol_ops)
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (平均 {r['duration_ms']/100:.2f}ms/条)")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # 7. 指标跑批 (21 项 × 10 次 = 210 次)
    print("[7] 指标跑批 (21 项 × 10 次 = 210 次)")
    def metrics_ops():
        collector = MetricsCollector(PMO_ROOT)
        for i in range(10):
            for mid in ["BIZ-M-001", "BIZ-M-002", "BIZ-M-003", "BIZ-M-004", "BIZ-M-005",
                        "GOV-M-001", "GOV-M-002", "GOV-M-003", "GOV-M-004", "GOV-M-005",
                        "GOV-M-006", "GOV-M-007", "GOV-M-008",
                        "ENG-M-001", "ENG-M-002", "ENG-M-003", "ENG-M-004", "ENG-M-005",
                        "ENG-M-006", "ENG-M-007", "ENG-M-008"]:
                collector.record(mid, float(i))
        return collector
    
    r = benchmark("指标 210 次", metrics_ops)
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (平均 {r['duration_ms']/210:.2f}ms/次)")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # 8. L2 审计 L1 (8 PMO 角色, DEC-2026-0002)
    print("[8] L2 6 agent 审计 L1 (三权分立 + 3 维度分离, DEC-2026-0002)")
    r = benchmark("L2 6 agent 审计 L1", lambda: pmo.l2_audit_l1())
    results.append(r)
    print(f"  - 耗时: {r['duration_ms']:.1f}ms (6 个 L2 审计 + Assessor + Message-Broker)")
    print(f"  - 内存增量: {r['memory_delta_mb']:.1f}MB\n")
    
    # ============================================
    # 性能基线报告
    # ============================================
    print("=" * 60)
    print("  性能基线报告")
    print("=" * 60)
    print(f"  {'项目':<30} {'耗时 (ms)':<15} {'内存 (MB)':<15}")
    print(f"  {'-'*30} {'-'*15} {'-'*15}")
    for r in results:
        print(f"  {r['name']:<30} {r['duration_ms']:>10.1f}     {r['memory_total_mb']:>10.1f}")
    
    total_duration = sum(r['duration_ms'] for r in results)
    total_mem = max(r['memory_total_mb'] for r in results)
    print(f"\n  总耗时: {total_duration:.1f}ms")
    print(f"  峰值内存: {total_mem:.1f}MB")
    
    # 性能基线
    print("\n  性能基线 (用于 m0.4 运维监控, DEC-2026-0002):")
    print(f"    - PMO 启动耗时基线: {results[0]['duration_ms']:.1f}ms")
    print(f"    - 8 agent 激活基线: {results[1]['duration_ms']:.1f}ms (平均 {results[1]['duration_ms']/8:.1f}ms/agent)")
    print(f"    - 维度 1 业务项目注册基线: {results[2]['duration_ms']/10:.2f}ms/项目 (10 项目)")
    print(f"    - 维度 2 研发 5 阶段采集基线: {results[3]['duration_ms']/50:.2f}ms/采集 (50 采集)")
    print(f"    - 维度 3 业务项目上报基线: {results[4]['duration_ms']/50:.2f}ms/上报 (50 上报)")
    print(f"    - Assessor 3 维度考核基线: {results[5]['duration_ms']/10:.2f}ms/考核 (10 考核)")
    print(f"    - Message-Broker 项目间消息基线: {results[6]['duration_ms']/100:.2f}ms/消息 (100 消息)")
    print(f"    - 业务流耗时基线: {results[7]['duration_ms']:.1f}ms (10 状态转换)")
    print(f"    - 异常拦截基线: {results[9]['duration_ms']/100:.2f}ms/次")
    print(f"    - 通信基线: {results[10]['duration_ms']/100:.2f}ms/条")
    print(f"    - 指标采集基线: {results[11]['duration_ms']/210:.2f}ms/次")
    print(f"    - L2 6 agent 审计 L1 基线: {results[12]['duration_ms']:.1f}ms")
    
    # 保存性能基线 (清理 result 中的 PMOInstance 等不可序列化对象)
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items() if k not in ["result", "pmo_instance", "pmo"]}
        elif isinstance(obj, list):
            return [clean_for_json(i) for i in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)  # 不可序列化对象转 str
    
    cleaned_results = clean_for_json(results)
    
    baseline_dir = Path(PMO_ROOT) / "metrics" / "engineering" / "1.1-pmo-self"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline_file = baseline_dir / "perf-baseline.json"
    with open(baseline_file, "w") as f:
        json.dump({
            "version": "0.3.0",
            "decision": "DEC-2026-0002",
            "agent_count": 8,
            "three_dimensions": ["业务项目整体", "研发 5 阶段", "业务项目上报"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {
                "python": sys.version.split()[0],
                "psutil": psutil.__version__ if HAS_PSUTIL else "not installed"
            },
            "results": cleaned_results
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  性能基线已保存: {baseline_file}")


if __name__ == "__main__":
    main()
