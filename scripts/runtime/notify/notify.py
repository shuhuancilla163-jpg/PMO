"""
PMO Sponsor 通知 (notify.py)
- 3 层告警 (0.0.10):
  - 业务内部 → 业务项目自给
  - 项目级 → PMO 实例
  - PMO 重大 → Sponsor
- 通知方式: 简报 / 指标看板 / 即时通知
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NotifyChannel(str, Enum):
    BRIEF = "brief"          # 简报 (阶段报告)
    DASHBOARD = "dashboard"  # 指标看板 (Sponsor 看)
    INSTANT = "instant"      # 即时通知 (重大异常)


class SponsorNotifier:
    """Sponsor 通知器"""
    
    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.notifications: List[Dict[str, Any]] = []
        self.sponsor_inbox: List[Dict[str, Any]] = []
    
    def notify_sponsor(self, channel: NotifyChannel, title: str, content: Dict[str, Any], severity: str = "info") -> Dict[str, Any]:
        """通知 Sponsor (顶层权威)"""
        notification = {
            "notification_id": f"NOTIF-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "channel": channel.value,
            "title": title,
            "content": content,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        }
        self.notifications.append(notification)
        # 重大异常才进 Sponsor 收件箱
        if channel == NotifyChannel.INSTANT or severity == "critical":
            self.sponsor_inbox.append(notification)
        return notification
    
    def notify_brief(self, title: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """简报 (阶段报告)"""
        return self.notify_sponsor(NotifyChannel.BRIEF, title, content, "info")
    
    def notify_dashboard(self, title: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """指标看板 (Sponsor 看)"""
        return self.notify_sponsor(NotifyChannel.DASHBOARD, title, content, "info")
    
    def notify_instant(self, title: str, content: Dict[str, Any], severity: str = "warning") -> Dict[str, Any]:
        """即时通知 (重大异常)"""
        return self.notify_sponsor(NotifyChannel.INSTANT, title, content, severity)
    
    def get_sponsor_inbox(self) -> List[Dict[str, Any]]:
        """Sponsor 收件箱"""
        return self.sponsor_inbox


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=== PMO Sponsor 通知演示 (3 层) ===\n")
    
    notifier = SponsorNotifier(PMO_ROOT)
    
    # 1. 简报 (阶段完成)
    print("[1] 简报 (阶段完成)")
    notifier.notify_brief(
        title="m0.1 PMO 存储层完成",
        content={"phase": "M0", "complexity": 4, "deliverables": 25, "status": "completed"}
    )
    print(f"  - 简报已发\n")
    
    # 2. 指标看板 (Sponsor 看)
    print("[2] 指标看板 (Sponsor 可看)")
    notifier.notify_dashboard(
        title="业务指标看板 (5 项)",
        content={
            "flow_latency": 0,
            "exception_rate": 0,
            "pass_rate": 0,
            "rollback_rate": 0,
            "token_consumption": 0
        }
    )
    print(f"  - 看板已更新\n")
    
    # 3. 即时通知 (重大异常, 进 Sponsor 收件箱)
    print("[3] 即时通知 (重大异常 → Sponsor 收件箱)")
    notifier.notify_instant(
        title="PMO 实例异常: 1.1 项目配额超限",
        content={"severity": "critical", "code": "P002", "biz_project": "1.1"},
        severity="critical"
    )
    print(f"  - 即时通知已发, 进 Sponsor 收件箱\n")
    
    # 4. Sponsor 收件箱
    inbox = notifier.get_sponsor_inbox()
    print(f"[4] Sponsor 收件箱: {len(inbox)} 条")
    for n in inbox:
        print(f"  - {n['title']} ({n['severity']})")
