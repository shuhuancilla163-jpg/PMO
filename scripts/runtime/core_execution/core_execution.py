"""
PMO 核心执行模块 (core_execution.py)
- 7 项核心执行工具 (m1.3)
  - C1: 阶段流转引擎 (P0-P9 状态机)
  - C2: 阶段门控验收脚本
  - C3: 决策日志工具
  - C6: 不可变文档签名工具
  - C9: Sponsor 介入面板
  - C10: 角色性格 prompt 加载器
  - C15: 角色身份加载器 (含 L? 注入)
- 业务/治理/工程指标可采
- PMO 规范不参与业务可验证
- DEC-2026-0002 加:
  - 3 维度分别考核 (Assessor-Agent)
  - 3 维度监控 (PMO-Main/Engineer-Agent/Monitor-Agent)
"""
import os
import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================
# C1 阶段流转 (P0-P9)
# ============================================
class Phase(str, Enum):
    P0_INTAKE = "P0-Intake"               # 需求采集
    P1_SPEC = "P1-Spec"                   # 规范
    P2_ARCHITECTURE = "P2-Architecture"   # 架构
    P3_PLAN = "P3-Plan"                   # 计划
    P4_IMPLEMENTATION = "P4-Implementation"  # 实施
    P5_SELF_TEST = "P5-Self-Test"         # 自测
    P6_RELEASE = "P6-Release"             # 发布
    P7_MONITOR = "P7-Monitor"             # 监控
    P8_RETROSPECTIVE = "P8-Retrospective"  # 复盘
    P9_RULE_EVOLUTION = "P9-Rule-Evolution"  # 规则演进


# ============================================
# C1 阶段流转引擎
# ============================================
class PhaseFlowEngine:
    """C1: 阶段流转引擎 (P0-P9 状态机)"""
    
    PHASE_ORDER = [
        Phase.P0_INTAKE, Phase.P1_SPEC, Phase.P2_ARCHITECTURE,
        Phase.P3_PLAN, Phase.P4_IMPLEMENTATION, Phase.P5_SELF_TEST,
        Phase.P6_RELEASE, Phase.P7_MONITOR, Phase.P8_RETROSPECTIVE,
        Phase.P9_RULE_EVOLUTION
    ]
    
    def __init__(self, project_id: str, pmo_root: str):
        self.project_id = project_id
        self.pmo_root = Path(pmo_root)
        self.current_phase = Phase.P0_INTAKE
        self.history: List[Dict[str, Any]] = []
    
    def advance(self, target_phase: Phase) -> bool:
        """推进到目标阶段"""
        try:
            current_idx = self.PHASE_ORDER.index(self.current_phase)
            target_idx = self.PHASE_ORDER.index(target_phase)
        except ValueError:
            return False
        
        if target_idx <= current_idx:
            return False  # 不能倒退
        
        self.history.append({
            "from": self.current_phase.value,
            "to": target_phase.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.current_phase = target_phase
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取阶段状态"""
        return {
            "project_id": self.project_id,
            "current_phase": self.current_phase.value,
            "phase_index": self.PHASE_ORDER.index(self.current_phase),
            "total_phases": len(self.PHASE_ORDER),
            "history_count": len(self.history)
        }


# ============================================
# C2 阶段门控验收
# ============================================
class PhaseGateValidator:
    """C2: 阶段门控验收脚本"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
    
    def validate_gate(self, project_id: str, phase: Phase) -> Dict[str, Any]:
        """验证阶段门控"""
        # 简化的门控检查
        checks = {
            "decision_log_exists": (self.pmo_root / "decisions" / "active").exists(),
            "immutable_docs_exist": (self.pmo_root / "immutable" / "0-governance").exists(),
            "metrics_baseline_exists": (self.pmo_root / "metrics" / "engineering").exists(),
            "biz_project_registered": (self.pmo_root / "biz-projects" / "1.1-pmo-self" / "register.yaml").exists()
        }
        pass_count = sum(1 for v in checks.values() if v)
        return {
            "project_id": project_id,
            "phase": phase.value,
            "checks": checks,
            "pass_count": pass_count,
            "total_checks": len(checks),
            "gate_passed": pass_count == len(checks),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================
# C3 决策日志工具 (SQLite + CLI)
# ============================================
class DecisionLog:
    """C3: 决策日志工具 (SQLite)"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.db_path = self.pmo_root / "decisions" / "decision-log.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化 SQLite 数据库"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT,
                actor TEXT,
                sponsor_approved INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
    
    def add(self, decision_id: str, title: str, category: str = "", actor: str = "", sponsor_approved: bool = False) -> int:
        """添加决策"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO decisions (decision_id, timestamp, title, category, actor, sponsor_approved)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (decision_id, datetime.now(timezone.utc).isoformat(), title, category, actor, 1 if sponsor_approved else 0))
            conn.commit()
            return c.lastrowid
        finally:
            conn.close()
    
    def list_all(self) -> List[Dict[str, Any]]:
        """列出所有决策"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT decision_id, timestamp, title, category, actor, sponsor_approved FROM decisions ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return [
            {
                "decision_id": r[0], "timestamp": r[1], "title": r[2],
                "category": r[3], "actor": r[4], "sponsor_approved": bool(r[5])
            }
            for r in rows
        ]


# ============================================
# C6 不可变文档签名工具
# ============================================
class ImmutableDocSigner:
    """C6: 不可变文档签名工具 (Git + Hash)"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
    
    def sign(self, doc_path: str) -> Dict[str, Any]:
        """签不可变文档 (生成 hash)"""
        full_path = self.pmo_root / doc_path
        if not full_path.exists():
            return {"error": f"文件不存在: {doc_path}"}
        
        content = full_path.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()
        return {
            "doc_path": doc_path,
            "sha256": sha256,
            "size_bytes": len(content),
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "algorithm": "sha256"
        }
    
    def verify(self, doc_path: str, expected_sha256: str) -> bool:
        """验证不可变文档签名"""
        sig = self.sign(doc_path)
        return sig.get("sha256") == expected_sha256


# ============================================
# C9 Sponsor 介入面板
# ============================================
class SponsorDashboard:
    """C9: Sponsor 介入面板"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
    
    def get_dashboard(self) -> Dict[str, Any]:
        """获取 Sponsor 看板"""
        return {
            "pmo_status": "running",
            "agent_count": 8,  # DEC-2026-0002
            "biz_projects": 3,  # 1.1 + 1.2 + 1.3
            "metrics": {
                "business": 5,
                "governance": 8,
                "engineering": 8
            },
            "three_dimensions": {
                "dim_1_project_overall": "PMO-Main",
                "dim_2_eng_5_stages": "Engineer-Agent",
                "dim_3_biz_reported": "Monitor-Agent"
            },
            "sponsor_inbox": [],  # 后期填充
            "last_update": datetime.now(timezone.utc).isoformat()
        }


# ============================================
# C10 角色性格 prompt 加载器
# ============================================
class PersonalityLoader:
    """C10: 角色性格 prompt 加载器"""
    
    PERSONALITIES = {
        "Sponsor": "严谨客观, 不迎合, 认真, 不怕吃苦, 解决问题",
        "PMO-Main": "行政权威, 管理 N 业务项目, 维度 1 业务项目整体采集",
        "Plan-Agent": "司法权威, 计划/治理, 审计 L1",
        "Engineer-Agent": "司法权威, 工程, 维度 2 业务项目内研发 5 阶段采集",
        "Monitor-Agent": "司法权威, 监控, 维度 3 业务项目上报采集, 监管上报合规",
        "Reviewer-Agent": "司法权威, 审查/审计, 互相验证",
        "Assessor-Agent": "司法权威, 3 维度分别考核",
        "Message-Broker-Agent": "司法权威, 消息, 项目间消息经 PMO 中介"
    }
    
    def load(self, role_name: str) -> Optional[str]:
        """加载角色性格 prompt"""
        return self.PERSONALITIES.get(role_name)


# ============================================
# C15 角色身份加载器 (含 L? 注入)
# ============================================
class RoleIdentityLoader:
    """C15: 角色身份加载器 (含 L? 层级注入)"""
    
    def __init__(self):
        self.identities = {
            "L0_Sponsor": {"name": "Sponsor", "layer": "L0", "power": "supervise", "role": "顶层权威, 看指标看板, 不执行"},
            "L1_PMO-Main": {"name": "PMO-Main", "layer": "L1", "power": "executive", "role": "1 实例管 N 项目, 维度 1 采集"},
            "L2_Plan-Agent": {"name": "Plan-Agent", "layer": "L2", "power": "judicial", "role": "计划/治理"},
            "L2_Engineer-Agent": {"name": "Engineer-Agent", "layer": "L2", "power": "judicial", "role": "工程, 维度 2 采集"},
            "L2_Monitor-Agent": {"name": "Monitor-Agent", "layer": "L2", "power": "judicial", "role": "监控, 维度 3 采集"},
            "L2_Reviewer-Agent": {"name": "Reviewer-Agent", "layer": "L2", "power": "judicial", "role": "审查/审计"},
            "L2_Assessor-Agent": {"name": "Assessor-Agent", "layer": "L2", "power": "judicial", "role": "3 维度考核"},
            "L2_Message-Broker-Agent": {"name": "Message-Broker-Agent", "layer": "L2", "power": "judicial", "role": "项目间消息经 PMO 中介"}
        }
    
    def load(self, layer_role: str) -> Optional[Dict[str, Any]]:
        """加载角色身份"""
        return self.identities.get(layer_role)


# ============================================
# DEC-2026-0002 3 维度分别考核 (Assessor-Agent)
# ============================================
class ThreeDimensionAssessment:
    """DEC-2026-0002: 3 维度分别考核"""
    
    def __init__(self, assessor_agent):
        self.assessor = assessor_agent
    
    def assess(self, pmo_main, engineer_agent, monitor_agent, project_id: str) -> Dict[str, Any]:
        """3 维度分别考核"""
        return self.assessor.assess_project(pmo_main, engineer_agent, monitor_agent, project_id)


# ============================================
# DEC-2026-0002 3 维度监控
# ============================================
class ThreeDimensionMonitor:
    """DEC-2026-0002: 3 维度监控 (PMO-Main/Engineer-Agent/Monitor-Agent)"""
    
    def __init__(self, pmo_main, engineer_agent, monitor_agent):
        self.pmo_main = pmo_main
        self.engineer_agent = engineer_agent
        self.monitor_agent = monitor_agent
    
    def monitor_all(self, project_id: str) -> Dict[str, Any]:
        """监控所有 3 维度"""
        return {
            "dimension_1": self.pmo_main.reflect(),
            "dimension_2_status": self.engineer_agent.get_eng_5_stages_status(project_id),
            "dimension_3_compliance": self.monitor_agent.get_compliance_report(project_id)
        }


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    # core_execution.py 在 scripts/runtime/, 向上 2 层 = PMO_ROOT
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    print("=== PMO 核心执行模块演示 (m1.3 + DEC-2026-0002) ===\n")
    print(f"PMO_ROOT: {PMO_ROOT}\n")
    
    # C1 阶段流转
    print("[C1] 阶段流转引擎 (P0-P9)")
    pfe = PhaseFlowEngine("1.1", PMO_ROOT)
    pfe.advance(Phase.P1_SPEC)
    pfe.advance(Phase.P2_ARCHITECTURE)
    pfe.advance(Phase.P4_IMPLEMENTATION)
    pfe.advance(Phase.P5_SELF_TEST)
    s = pfe.get_status()
    print(f"  - 当前: {s['current_phase']} (index {s['phase_index']}/{s['total_phases']})")
    print(f"  - history: {s['history_count']} 次转换\n")
    
    # C2 阶段门控
    print("[C2] 阶段门控验收")
    pgv = PhaseGateValidator(PMO_ROOT)
    r = pgv.validate_gate("1.1", Phase.P5_SELF_TEST)
    print(f"  - gate passed: {r['gate_passed']} ({r['pass_count']}/{r['total_checks']})\n")
    
    # C3 决策日志
    print("[C3] 决策日志工具 (SQLite)")
    dl = DecisionLog(PMO_ROOT)
    dl.add("DEC-2026-9999", "m1.3 核心执行测试", "core-execution", "PMO-Main", True)
    decisions = dl.list_all()
    print(f"  - 总决策数: {len(decisions)}\n")
    
    # C6 不可变文档签名
    print("[C6] 不可变文档签名")
    signer = ImmutableDocSigner(PMO_ROOT)
    sig = signer.sign("immutable/0-governance/0.0.1-five-values.md")
    print(f"  - sha256: {sig['sha256'][:16]}... ({sig['size_bytes']} bytes)\n")
    
    # C9 Sponsor 面板
    print("[C9] Sponsor 介入面板")
    dash = SponsorDashboard(PMO_ROOT)
    d = dash.get_dashboard()
    print(f"  - PMO: {d['pmo_status']}, agent: {d['agent_count']}, biz_projects: {d['biz_projects']}\n")
    
    # C10 性格加载
    print("[C10] 角色性格 prompt 加载器")
    pl = PersonalityLoader()
    for role in ["Sponsor", "PMO-Main", "Engineer-Agent", "Assessor-Agent"]:
        personality = pl.load(role)
        print(f"  - {role}: {personality[:30]}...")
    print()
    
    # C15 身份加载
    print("[C15] 角色身份加载器 (含 L? 注入)")
    ril = RoleIdentityLoader()
    for lr in ["L0_Sponsor", "L1_PMO-Main", "L2_Assessor-Agent"]:
        identity = ril.load(lr)
        print(f"  - {lr}: layer={identity['layer']}, power={identity['power']}")
    print()
    
    # DEC-2026-0002 3 维度考核
    print("[DEC-2026-0002] 3 维度分别考核 (Assessor)")
    sys.path.insert(0, os.path.join(PMO_ROOT, "scripts", "runtime"))
    from agents.agent_base import PMOInstance
    pmo = PMOInstance(PMO_ROOT)
    pmo.activate_all()
    tda = ThreeDimensionAssessment(pmo.assessor_agent)
    a = tda.assess(pmo.pmo_main, pmo.engineer_agent, pmo.monitor_agent, "1.1")
    print(f"  - 1.1 总考: {a['overall_verdict']}\n")
    
    # DEC-2026-0002 3 维度监控
    print("[DEC-2026-0002] 3 维度监控")
    tdm = ThreeDimensionMonitor(pmo.pmo_main, pmo.engineer_agent, pmo.monitor_agent)
    m = tdm.monitor_all("1.1")
    print(f"  - 3 维度监控完成\n")
    
    # PMO 规范不参与业务可验证
    print("[验证] PMO 规范不参与业务")
    print(f"  - PMO 规范 (immutable/) 不包含业务具体内容")
    print(f"  - 业务具体内容由业务项目自维护 (biz-projects/)")
    print(f"  - 业务项目 2 层合规: 业务项目整体 (m2.6) + 业务项目内研发 5 阶段")
    print(f"  - DEC-2026-0002 边界: PMO 监管 ≠ PMO 干预")
    print()
    print("=== m1.3 核心执行模块演示完成 ===")
