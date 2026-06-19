"""
PMO 运维模块 (operations.py)
- 监控 (m0.4)
- 告警 3 层 (业务自给 / PMO 实例 / Sponsor)
- 恢复 (业务项目恢复 + PMO 实例恢复)
- 3 层异常拦截 (PMO 规范不参与业务, PMO 实例拦截项目级, 业务项目拦截自身)
- Token 预算按业务项目分
- 灾备 (业务项目备份 + 恢复)
- 指标监控 (3 维度: 业务项目整体 / 研发 5 阶段 / 业务项目上报)

DEC-2026-0002: 3 维度监控 + 8 PMO 角色 + 3 维度考核
"""
import os
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================
# 告警层级 (3 层, 0.0.10)
# ============================================
class AlertLevel(str, Enum):
    BIZ_SELF = "biz-self"          # 业务自给 (业务项目自处理)
    PMO_INSTANCE = "pmo"            # PMO 实例 (升级到 PMO)
    SPONSOR = "sponsor"             # Sponsor (PMO 重大异常升级)


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ============================================
# 3 层异常拦截层 (DEC-2026-0002 边界清晰化)
# ============================================
class ExceptionLayer(str, Enum):
    PMO_SPEC = "pmo-spec"           # L0 PMO 规范 (不参与业务, 只标准+监督)
    PMO_INSTANCE = "pmo-instance"   # L1 PMO 实例 (拦截研发异常 + 项目异常)
    BIZ_PROJECT = "biz-project"     # L2 业务项目 (拦截业务异常)


# ============================================
# 恢复策略
# ============================================
class RecoveryStrategy(str, Enum):
    RETRY = "retry"                  # 重试
    FALLBACK = "fallback"            # 降级
    RESTART = "restart"              # 重启
    ROLLBACK = "rollback"            # 回滚
    ESCALATE = "escalate"            # 升级
    SKIP = "skip"                    # 跳过


# ============================================
# 运维监控器 (m0.4)
# ============================================
class OperationsMonitor:
    """PMO 运维监控器 (m0.4)
    
    监控 3 维度 (DEC-2026-0002):
    - 维度 1: 业务项目整体 (PMO-Main)
    - 维度 2: 业务项目内研发 5 阶段 (Engineer-Agent)
    - 维度 3: 业务项目内业务上报 (Monitor-Agent)
    """
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.alerts: List[Dict[str, Any]] = []
        self.recoveries: List[Dict[str, Any]] = []
        self.disaster_backups: List[Dict[str, Any]] = []
    
    def monitor_project_state(self, project_id: str, state: str) -> Dict[str, Any]:
        """监控业务项目状态 (维度 1)"""
        valid_states = ["registered", "active", "paused", "blocked", "completed", "archived", "canceled"]
        status = "ok" if state in valid_states else "violation"
        result = {
            "monitor": "project_state",
            "project_id": project_id,
            "dimension": 1,
            "state": state,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if status == "violation":
            self.trigger_alert(AlertLevel.PMO_INSTANCE, AlertSeverity.WARNING, "STATE001", f"业务项目 {project_id} 状态非法: {state}")
        return result
    
    def monitor_metrics_5(self, project_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """监控业务项目 5 项基础指标 (维度 3)"""
        required = ["flow_latency", "exception_rate", "pass_rate", "rollback_rate", "token_consumption"]
        missing = [m for m in required if m not in metrics]
        result = {
            "monitor": "metrics_5_basic",
            "project_id": project_id,
            "dimension": 3,
            "missing_metrics": missing,
            "status": "ok" if not missing else "violation",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if missing:
            self.trigger_alert(AlertLevel.PMO_INSTANCE, AlertSeverity.WARNING, "METRICS001", f"业务项目 {project_id} 5 项基础指标缺失: {missing}")
        return result
    
    def monitor_token_budget(self, project_id: str, used: int, quota: int) -> Dict[str, Any]:
        """监控业务项目 Token 预算"""
        usage_pct = (used / quota * 100) if quota > 0 else 0
        result = {
            "monitor": "token_budget",
            "project_id": project_id,
            "used": used,
            "quota": quota,
            "usage_pct": f"{usage_pct:.2f}%",
            "status": "ok" if usage_pct < 80 else ("warning" if usage_pct < 100 else "critical"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if usage_pct >= 80:
            severity = AlertSeverity.WARNING if usage_pct < 100 else AlertSeverity.CRITICAL
            self.trigger_alert(AlertLevel.PMO_INSTANCE, severity, "TOKEN001", f"业务项目 {project_id} Token 使用 {usage_pct:.1f}%")
        return result
    
    def trigger_alert(self, level: AlertSeverity, severity: AlertSeverity, code: str, message: str, project_id: str = "") -> Dict[str, Any]:
        """触发告警 (3 层)"""
        alert = {
            "alert_id": f"ALERT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{code}",
            "level": level.value,
            "severity": severity.value,
            "code": code,
            "message": message,
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.alerts.append(alert)
        return alert
    
    def execute_recovery(self, project_id: str, strategy: RecoveryStrategy, reason: str) -> Dict[str, Any]:
        """执行恢复"""
        recovery = {
            "recovery_id": f"RECOV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "strategy": strategy.value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.recoveries.append(recovery)
        return recovery
    
    def disaster_backup(self, project_id: str, source_path: str) -> Dict[str, Any]:
        """灾备: 业务项目备份"""
        backup_id = f"BACKUP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        backup_dir = self.pmo_root / "archive" / "disaster-backups" / project_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        # 简化的备份记录 (实际项目可能用 tar/zip)
        backup = {
            "backup_id": backup_id,
            "project_id": project_id,
            "source_path": source_path,
            "backup_path": str(backup_dir),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.disaster_backups.append(backup)
        return backup
    
    def get_operations_report(self) -> Dict[str, Any]:
        """获取运维报告"""
        return {
            "alerts_count": len(self.alerts),
            "recoveries_count": len(self.recoveries),
            "disaster_backups_count": len(self.disaster_backups),
            "alerts_by_level": {
                "biz-self": sum(1 for a in self.alerts if a["level"] == "biz-self"),
                "pmo": sum(1 for a in self.alerts if a["level"] == "pmo"),
                "sponsor": sum(1 for a in self.alerts if a["level"] == "sponsor")
            },
            "alerts_by_severity": {
                "info": sum(1 for a in self.alerts if a["severity"] == "info"),
                "warning": sum(1 for a in self.alerts if a["severity"] == "warning"),
                "critical": sum(1 for a in self.alerts if a["severity"] == "critical")
            }
        }


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO 运维演示 (m0.4) ===\n")
    
    op = OperationsMonitor(PMO_ROOT)
    
    # 1. 维度 1 业务项目状态监控
    print("[1] 维度 1 业务项目状态监控")
    r = op.monitor_project_state("1.1", "active")
    print(f"  - 1.1 状态: {r['status']}")
    r = op.monitor_project_state("1.2", "invalid_state")
    print(f"  - 1.2 状态: {r['status']}\n")
    
    # 2. 维度 3 业务项目 5 项基础指标监控
    print("[2] 维度 3 业务项目 5 项基础指标监控")
    r = op.monitor_metrics_5("1.1", {"flow_latency": 100, "exception_rate": 0.01, "pass_rate": 0.99, "rollback_rate": 0.001, "token_consumption": 10000})
    print(f"  - 1.1 指标: {r['status']}")
    r = op.monitor_metrics_5("1.2", {"flow_latency": 100})  # 缺 4 项
    print(f"  - 1.2 指标: {r['status']}, 缺: {r['missing_metrics']}\n")
    
    # 3. Token 预算监控
    print("[3] Token 预算监控")
    r = op.monitor_token_budget("1.1", used=10000, quota=100000)
    print(f"  - 1.1 Token: {r['status']}, 使用率 {r['usage_pct']}")
    r = op.monitor_token_budget("1.2", used=90000, quota=100000)
    print(f"  - 1.2 Token: {r['status']}, 使用率 {r['usage_pct']}\n")
    
    # 4. 恢复执行
    print("[4] 恢复执行")
    r = op.execute_recovery("1.1", RecoveryStrategy.RETRY, "1.1 业务流重试")
    print(f"  - 1.1 恢复: {r['strategy']} ({r['recovery_id']})\n")
    
    # 5. 灾备
    print("[5] 灾备")
    r = op.disaster_backup("1.1", "biz-projects/1.1-pmo-self/")
    print(f"  - 1.1 灾备: {r['backup_id']}\n")
    
    # 6. 运维报告
    print("[6] 运维报告")
    report = op.get_operations_report()
    print(f"  - 告警数: {report['alerts_count']}")
    print(f"  - 恢复数: {report['recoveries_count']}")
    print(f"  - 灾备数: {report['disaster_backups_count']}")
    print(f"  - 告警按层级: {report['alerts_by_level']}")
    print(f"  - 告警按严重性: {report['alerts_by_severity']}")
    print()
    print("=== m0.4 运维演示完成 ===")
