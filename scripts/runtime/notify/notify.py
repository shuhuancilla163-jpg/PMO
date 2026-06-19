"""
PMO Sponsor 通知 (notify.py)
- 3 层告警 (0.0.10):
  - 业务内部 → 业务项目自给
  - 项目级 → PMO 实例
  - PMO 重大 → Sponsor
- 通知方式: 简报 / 指标看板 / 即时通知 / Webhook / 磁盘持久化
"""
import json
import os
import urllib.request
import urllib.error
import ssl
import hmac
import hashlib
import base64
import time
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


# ============================================
# Webhook 推送器
# ============================================
class WebhookNotifier:
    """Webhook 推送器 — 将 Sponsor 通知推送到配置的 Webhook URL"""

    def __init__(self, webhook_url: Optional[str] = None, config_path: Optional[str] = None):
        self.webhook_url = webhook_url
        self.enabled = False

        if config_path:
            self._load_from_config(config_path)
        elif webhook_url:
            self.webhook_url = webhook_url
            self.enabled = True

        self._pmo_root = None

    def _load_from_config(self, config_path: str) -> None:
        """从 notify.json 配置文件加载 Webhook URL
        环境变量优先级高于配置文件（用于 GitHub Secrets 等 CI/CD 场景）:
          FEISHU_WEBHOOK_URL
          FEISHU_WEBHOOK_SECRET
          FEISHU_WEBHOOK_ENABLED
        """
        config_file = Path(config_path)
        config = {}
        if config_file.exists():
            import json as _json
            with open(config_file, "r", encoding="utf-8") as f:
                config = _json.load(f)

        webhook_cfg = config.get("sponsor_notify", {}).get("webhook", {})

        self.webhook_url = (
            os.environ.get("FEISHU_WEBHOOK_URL")
            or webhook_cfg.get("url", "")
        )
        self.secret = (
            os.environ.get("FEISHU_WEBHOOK_SECRET")
            or webhook_cfg.get("secret", "")
        )
        self.enabled = (
            os.environ.get("FEISHU_WEBHOOK_ENABLED", "").lower() in ("true", "1", "yes")
            or webhook_cfg.get("enabled", False)
        ) and bool(self.webhook_url)
        self.platform = "feishu"


    def push(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """同步推送通知到 Webhook"""
        if not self.enabled or not self.webhook_url:
            return {"status": "skipped", "reason": "webhook disabled or not configured"}

        payload = self._build_payload(notification)
        platform = getattr(self, "platform", "generic")

        if platform == "feishu" and self.secret:
            sign_fields = self._feishu_sign_headers()
            payload_dict = json.loads(payload)
            payload_dict.update(sign_fields)
            payload = json.dumps(payload_dict)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PMO-SponsorNotifier/1.0"
        }

        try:
            req = urllib.request.Request(
                self.webhook_url,
                data=payload.encode("utf-8"),
                headers=headers,
                method="POST"
            )
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                response_text = resp.read().decode("utf-8", errors="replace")
                return {
                    "status": "success",
                    "http_status": resp.status,
                    "response": response_text[:200]
                }
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            return {"status": "failed", "http_status": e.code, "response": body[:200]}
        except urllib.error.URLError as e:
            return {"status": "error", "reason": f"url_error: {e.reason}"}

    def _build_payload(self, notification: Dict[str, Any]) -> str:
        """根据平台构建 Webhook payload"""
        platform = getattr(self, "platform", "generic")

        if platform == "feishu":
            return self._build_feishu_payload(notification)
        else:
            return json.dumps({
                "event": "pmo_sponsor_notification",
                "notification": notification,
                "source": "PMO-L1-SponsorNotifier",
                "sent_at": datetime.now(timezone.utc).isoformat()
            })

    def _feishu_sign_headers(self) -> Dict[str, str]:
        """生成飞书签名校验头 (timestamp + sign)
        飞书文档: 用 timestamp + "\\n" + secret 作为 HMAC-SHA256 密钥，对空字符串签名
        """
        timestamp = str(int(time.time()))
        key = f"{timestamp}\n{self.secret}"
        sign = base64.b64encode(
            hmac.new(key.encode("utf-8"), b"", hashlib.sha256).digest()
        ).decode("utf-8")
        return {"timestamp": timestamp, "sign": sign}

    def _build_feishu_payload(self, notification: Dict[str, Any]) -> str:
        """构建飞书富文本消息 payload"""
        severity = notification.get("severity", "info")
        channel = notification.get("channel", "")
        title = notification.get("title", "")
        content = notification.get("content", {})
        notif_id = notification.get("notification_id", "")
        timestamp = notification.get("timestamp", "")

        severity_emoji = {
            "critical": "🔴 CRITICAL",
            "warning": "🟡 WARNING",
            "info": "ℹ️ INFO",
        }.get(severity, severity.upper())

        lines = [
            f"**{severity_emoji} PMO 通知**",
            f"**标题:** {title}",
            f"**渠道:** {channel}",
            f"**通知ID:** {notif_id}",
            f"**时间:** {timestamp}",
        ]

        if content:
            lines.append("**内容:**")
            if isinstance(content, dict):
                for k, v in content.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"  {content}")

        return json.dumps({
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"{severity_emoji} {title}",
                        "content": [[
                            {"tag": "text", "text": line}
                            for line in lines
                        ]]
                    }
                }
            }
        })


# ============================================
# 磁盘持久化
# ============================================
class InboxPersistence:
    """Sponsor 收件箱磁盘持久化"""

    INBOX_FILE = "inbox.json"

    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.inbox_file = self.pmo_root / "logs" / "notify" / self.INBOX_FILE
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.inbox_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, inbox: List[Dict[str, Any]]) -> None:
        """保存收件箱到磁盘"""
        with open(self.inbox_file, "w", encoding="utf-8") as f:
            json.dump({
                "inbox": inbox,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }, f, ensure_ascii=False, indent=2)

    def load(self) -> List[Dict[str, Any]]:
        """从磁盘加载收件箱"""
        if not self.inbox_file.exists():
            return []
        try:
            with open(self.inbox_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("inbox", [])
        except (json.JSONDecodeError, IOError):
            return []

    def append(self, notification: Dict[str, Any]) -> None:
        """追加单条通知到磁盘"""
        inbox = self.load()
        inbox.append(notification)
        self.save(inbox)


class SponsorNotifier:
    """Sponsor 通知器 (含 Webhook 推送 + 磁盘持久化)"""

    def __init__(self, pmo_root: str, webhook_config_path: Optional[str] = None):
        self.pmo_root = Path(pmo_root)
        self.notifications: List[Dict[str, Any]] = []
        self.sponsor_inbox: List[Dict[str, Any]] = []

        self.webhook = WebhookNotifier(config_path=webhook_config_path)
        self.persistence = InboxPersistence(pmo_root)

        inbox_from_disk = self.persistence.load()
        if inbox_from_disk:
            self.sponsor_inbox = inbox_from_disk

    def notify_sponsor(self, channel: NotifyChannel, title: str, content: Dict[str, Any], severity: str = "info") -> Dict[str, Any]:
        """通知 Sponsor (顶层权威)"""
        notification = {
            "notification_id": f"NOTIF-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            "channel": channel.value,
            "title": title,
            "content": content,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        }
        self.notifications.append(notification)

        is_inbox = channel == NotifyChannel.INSTANT or severity == "critical"
        if is_inbox:
            self.sponsor_inbox.append(notification)
            self.persistence.append(notification)
            webhook_result = self.webhook.push(notification)
            notification["_webhook"] = webhook_result

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

    def mark_read(self, notification_id: str) -> bool:
        """标记通知为已读"""
        for n in self.sponsor_inbox:
            if n["notification_id"] == notification_id:
                n["read"] = True
                self.persistence.save(self.sponsor_inbox)
                return True
        return False

    def get_unread_count(self) -> int:
        """未读通知数量"""
        return sum(1 for n in self.sponsor_inbox if not n["read"])


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    CONFIG_PATH = os.path.join(PMO_ROOT, "config", "notify.json")

    # 加载 Webhook 配置 (json 格式，兼容无 yaml 环境)
    webhook_cfg = {"enabled": False, "url": ""}
    config_file = Path(CONFIG_PATH)
    if config_file.exists():
        import json as _json
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = _json.load(f)
            webhook_cfg = cfg.get("sponsor_notify", {}).get("webhook", {"enabled": False, "url": ""})

    print("=== PMO Sponsor 通知演示 (3 层 + Webhook + 磁盘持久化) ===\n")
    print(f"[Webhook] enabled={webhook_cfg['enabled']}, url={webhook_cfg.get('url', 'N/A')}\n")

    notifier = SponsorNotifier(PMO_ROOT, webhook_config_path=CONFIG_PATH)

    # 1. 简报 (阶段完成) — 不进收件箱
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

    # 3. 即时通知 (重大异常 → Sponsor 收件箱 + 磁盘持久化 + Webhook)
    print("[3] 即时通知 (重大异常 → 收件箱 + 持久化 + Webhook)")
    result = notifier.notify_instant(
        title="PMO 实例异常: 1.1 项目配额超限",
        content={"severity": "critical", "code": "P002", "biz_project": "1.1"},
        severity="critical"
    )
    print(f"  - 即时通知已发, 进 Sponsor 收件箱")
    if result.get("_webhook"):
        wh = result["_webhook"]
        print(f"  - Webhook: {wh.get('status', 'unknown')}")
    print()

    # 4. Sponsor 收件箱
    inbox = notifier.get_sponsor_inbox()
    print(f"[4] Sponsor 收件箱: {len(inbox)} 条 (磁盘: {notifier.persistence.inbox_file})")
    for n in inbox:
        print(f"  - {n['title']} ({n['severity']})")

    # 5. 未读数
    print(f"\n[5] 未读通知: {notifier.get_unread_count()} 条")
