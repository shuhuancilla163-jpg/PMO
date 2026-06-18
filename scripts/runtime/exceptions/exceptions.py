"""
PMO 异常拦截 (exceptions.py)
- 3 层异常拦截 (0.0.10)
  - L0 PMO 规范: 不参与业务, 标准+监督
  - L1 PMO 实例: 拦截项目级 (含自身)
  - L2 业务项目: 拦截自身
- 4 类业务异常: 业务/系统/合规/性能
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_machine import ExceptionLayer, ExceptionSeverity


# ============================================
# 业务异常 4 类 (Q7)
# ============================================
class BizExceptionType(str, Enum):
    BIZ = "biz"            # 业务异常 (业务逻辑错误)
    SYSTEM = "system"      # 系统异常 (技术故障)
    COMPLIANCE = "compliance"  # 合规异常 (违规)
    PERFORMANCE = "performance"  # 性能异常 (SLA 失败)


# ============================================
# PMO 异常
# ============================================
class PMOException:
    """PMO 异常基类"""
    
    def __init__(self, layer: ExceptionLayer, severity: ExceptionSeverity, code: str, message: str, source: str = ""):
        self.exception_id = f"EXC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{code}"
        self.layer = layer
        self.severity = severity
        self.code = code
        self.message = message
        self.source = source
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.handled = False
        self.handled_by = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "exception_id": self.exception_id,
            "layer": self.layer.value,
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp,
            "handled": self.handled,
            "handled_by": self.handled_by
        }


# ============================================
# 业务异常
# ============================================
class BizException(PMOException):
    """业务异常 (业务项目拦截自身)"""
    
    def __init__(self, biz_type: BizExceptionType, severity: ExceptionSeverity, code: str, message: str, biz_project: str = ""):
        super().__init__(ExceptionLayer.BIZ_PROJECT, severity, code, message, source=biz_project)
        self.biz_type = biz_type


# ============================================
# PMO 实例异常
# ============================================
class PMOInstanceException(PMOException):
    """PMO 实例异常 (PMO 实例拦截项目级, 含自身)"""
    
    def __init__(self, severity: ExceptionSeverity, code: str, message: str, source: str = ""):
        super().__init__(ExceptionLayer.PMO_INSTANCE, severity, code, message, source=source)


# ============================================
# 异常拦截器 (3 层)
# ============================================
class ExceptionInterceptor:
    """3 层异常拦截器 (0.0.10)"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.exceptions: List[PMOException] = []
        self.intercepted_count = {ExceptionLayer.BIZ_PROJECT: 0, ExceptionLayer.PMO_INSTANCE: 0, ExceptionLayer.PMO_SPEC: 0}
        self.escalated_count = 0
    
    def intercept_biz(self, biz_type: BizExceptionType, severity: ExceptionSeverity, code: str, message: str, biz_project: str = "") -> BizException:
        """拦截业务异常 (L2 业务项目拦截自身)"""
        exc = BizException(biz_type, severity, code, message, biz_project)
        exc.handled = True
        exc.handled_by = "biz_project"
        self.exceptions.append(exc)
        self.intercepted_count[ExceptionLayer.BIZ_PROJECT] += 1
        print(f"[L2-biz-project] ✅ 业务异常已拦截: {exc.exception_id} ({biz_type.value}/{severity.value})")
        # 严重异常升级到 PMO 实例
        if severity in [ExceptionSeverity.CRITICAL]:
            self.escalate_to_pmo(exc)
        return exc
    
    def intercept_pmo(self, severity: ExceptionSeverity, code: str, message: str, source: str = "") -> PMOInstanceException:
        """拦截 PMO 实例异常 (L1 PMO 实例拦截项目级, 含自身)"""
        exc = PMOInstanceException(severity, code, message, source)
        exc.handled = True
        exc.handled_by = "pmo_instance"
        self.exceptions.append(exc)
        self.intercepted_count[ExceptionLayer.PMO_INSTANCE] += 1
        print(f"[L1-pmo-instance] ✅ PMO 实例异常已拦截: {exc.exception_id} ({severity.value})")
        # 严重异常升级到 Sponsor
        if severity in [ExceptionSeverity.CRITICAL]:
            self.escalate_to_sponsor(exc)
        return exc
    
    def escalate_to_pmo(self, biz_exc: BizException):
        """业务异常升级到 PMO 实例"""
        self.escalated_count += 1
        print(f"[L2→L1] 升级: {biz_exc.exception_id} (业务严重异常→PMO 实例)")
    
    def escalate_to_sponsor(self, pmo_exc: PMOInstanceException):
        """PMO 实例异常升级到 Sponsor"""
        self.escalated_count += 1
        print(f"[L1→L0] 升级: {pmo_exc.exception_id} (PMO 重大异常→Sponsor)")
    
    def pmo_spec_audit(self):
        """PMO 规范审计 (L0 PMO 规范, 不参与业务, 只监督)"""
        print(f"[L0-pmo-spec] 📋 PMO 规范审计中 (标准+监督, 不参与业务)...")
        return {
            "audit_type": "pmo_spec",
            "verdict": "compliant",
            "scope": "标准制定 + 监督, 不参与业务",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """拦截统计 (供指标看板用)"""
        return {
            "total": len(self.exceptions),
            "by_layer": {k.value: v for k, v in self.intercepted_count.items()},
            "escalated": self.escalated_count,
            "biz_exceptions_by_type": {
                bt.value: sum(1 for e in self.exceptions if isinstance(e, BizException) and e.biz_type == bt)
                for bt in BizExceptionType
            }
        }


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO 3 层异常拦截演示 ===\n")
    
    interceptor = ExceptionInterceptor(PMO_ROOT)
    
    # 1. L2 业务项目拦截自身
    print("[1] L2 业务项目拦截 (4 类业务异常)")
    interceptor.intercept_biz(BizExceptionType.BIZ, ExceptionSeverity.WARNING, "B001", "业务逻辑错误: 步骤顺序错", "1.1-pmo-self")
    interceptor.intercept_biz(BizExceptionType.SYSTEM, ExceptionSeverity.ERROR, "B002", "数据库连接失败", "1.1-pmo-self")
    interceptor.intercept_biz(BizExceptionType.COMPLIANCE, ExceptionSeverity.WARNING, "B003", "PII 数据未脱敏", "1.1-pmo-self")
    interceptor.intercept_biz(BizExceptionType.PERFORMANCE, ExceptionSeverity.CRITICAL, "B004", "业务流耗时 > 300s", "1.1-pmo-self")
    print()
    
    # 2. L1 PMO 实例拦截项目级
    print("[2] L1 PMO 实例拦截项目级 (含自身)")
    interceptor.intercept_pmo(ExceptionSeverity.WARNING, "P001", "业务项目 1.1 配额使用 80%")
    interceptor.intercept_pmo(ExceptionSeverity.CRITICAL, "P002", "业务项目 1.1 异常率超 20%")
    print()
    
    # 3. L0 PMO 规范审计
    print("[3] L0 PMO 规范 (不参与业务, 标准+监督)")
    audit = interceptor.pmo_spec_audit()
    print(f"  - 审计结果: {audit['verdict']}")
    print(f"  - 范围: {audit['scope']}\n")
    
    # 4. 拦截统计
    print("[4] 拦截统计 (供 Sponsor 指标看板)")
    stats = interceptor.get_statistics()
    print(f"  - 总异常: {stats['total']}")
    print(f"  - L0 规范审计: {stats['by_layer']['L0-pmo-spec']} (不拦截业务)")
    print(f"  - L1 PMO 实例拦截: {stats['by_layer']['L1-pmo-instance']}")
    print(f"  - L2 业务项目拦截: {stats['by_layer']['L2-biz-project']}")
    print(f"  - 升级次数: {stats['escalated']}")
    print(f"  - 业务异常按类型: {stats['biz_exceptions_by_type']}")
