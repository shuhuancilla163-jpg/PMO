"""
PMO Schema Watcher (schema_watcher.py, m0.8, DEC-2026-0008)
- 监听 config/biz-meta/ 下 E2-schema-*.json、E3-glossary-*.json
- 监听 config/data-sync.yaml
- 检测 sha256 hash 变化或 version 字段递增
- 生成变更事件写入 logs/schema-watcher/change-events-YYYYMMDD.json
- 通过 Message-Broker 发轻量 Ping 到 pmo.schema.change（不发完整内容）
- 维护 ACK 状态，超时 7 天告警
- PMO 不主动 Push 内容，业务系统主动 Pull
"""
import hashlib
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class ChangeSeverity(str, Enum):
    """变更严重级别"""
    INFO = "info"          # 普通变更
    BREAKING = "breaking"  # 破坏性变更
    CRITICAL = "critical"  # 关键变更


class SchemaWatcher:
    """PMO Schema Watcher — 监听 E2/E3/data-sync.yaml 变更，生成事件

    核心原则 (m0.8):
    - PMO 不主动 Push 内容，只发轻量 Ping
    - 业务系统主动 Pull 完整变更
    - 所有消息经 Message-Broker，可监控 + 可审计
    """

    PROTOCOL_VERSION = "0.8.0"
    PMO_SCHEMA_CHANGE_TOPIC = "pmo.schema.change"
    PMO_SCHEMA_ACK_TOPIC = "biz.{biz_project_id}.schema.ack"

    # 监听文件模式
    E2_PATTERN = re.compile(r"^E2-schema-.+\.json$")
    E3_PATTERN = re.compile(r"^E3-glossary-.+\.json$")
    DATA_SYNC_FILE = "data-sync.yaml"

    # ACK 超时（天）
    ACK_TIMEOUT_DAYS = 7

    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.biz_meta_dir = self.pmo_root / "config" / "biz-meta"
        self.data_sync_file = self.pmo_root / "config" / "data-sync.yaml"
        self.events_dir = self.pmo_root / "logs" / "schema-watcher"
        self.events_dir.mkdir(parents=True, exist_ok=True)

        # 状态
        self._file_hashes: Dict[str, str] = {}
        self._file_versions: Dict[str, str] = {}
        self._event_seq = 0
        self._pending_acks: Dict[str, Dict[str, Any]] = {}
        self._event_counter_file = self.events_dir / ".event_seq"
        self._load_event_seq()

        # Message-Broker（lazy init）
        self._broker = None

        # 初始化 hash 快照
        self._init_snapshots()

    # ---------------- Broker 懒加载 ----------------
    @property
    def broker(self):
        """懒加载 Message-Broker"""
        if self._broker is None:
            from protocol.message_broker import MessageBroker
            self._broker = MessageBroker(str(self.pmo_root))
        return self._broker

    # ---------------- 初始化快照 ----------------
    def _init_snapshots(self):
        """初始化文件 hash + version 快照（只存内存，不写文件）"""
        # E2 / E3 文件
        if self.biz_meta_dir.exists():
            for f in self.biz_meta_dir.iterdir():
                if f.is_file():
                    self._capture_snapshot(f)

        # data-sync.yaml
        if self.data_sync_file.exists():
            self._capture_snapshot(self.data_sync_file)

    def _capture_snapshot(self, path: Path):
        """记录单个文件的 hash + version"""
        key = str(path)
        try:
            content = path.read_text(encoding="utf-8")
            self._file_hashes[key] = self._sha256(content)
            # 尝试读 version 字段
            version = self._extract_version(content, path.suffix)
            if version:
                self._file_versions[key] = version
        except Exception:
            pass

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _extract_version(self, content: str, suffix: str) -> Optional[str]:
        """从文件内容中提取 version 字段"""
        if suffix == ".json":
            try:
                data = json.loads(content)
                return data.get("version") or data.get("data", {}).get("version")
            except Exception:
                pass
        return None

    # ---------------- 事件序号持久化 ----------------
    def _load_event_seq(self):
        """从文件加载事件序号"""
        try:
            if self._event_counter_file.exists():
                self._event_seq = int(self._event_counter_file.read_text().strip())
        except Exception:
            self._event_seq = 0

    def _save_event_seq(self):
        """保存事件序号到文件"""
        try:
            self._event_counter_file.write_text(str(self._event_seq))
        except Exception:
            pass

    # ---------------- 变更检测 ----------------
    def check_for_changes(self) -> List[Dict[str, Any]]:
        """主动检测文件变更，返回变更事件列表"""
        events = []
        current_time = datetime.now(timezone.utc)

        # 1. E2 / E3 文件
        if self.biz_meta_dir.exists():
            for f in self.biz_meta_dir.iterdir():
                if not f.is_file():
                    continue
                event = self._check_file(f, current_time)
                if event:
                    events.append(event)

        # 2. data-sync.yaml
        if self.data_sync_file.exists():
            event = self._check_file(self.data_sync_file, current_time)
            if event:
                events.append(event)

        # 3. 处理每个事件
        for ev in events:
            self._handle_change_event(ev)

        return events

    def _check_file(self, path: Path, current_time: datetime) -> Optional[Dict[str, Any]]:
        """检测单个文件是否有变更"""
        key = str(path)
        try:
            content = path.read_text(encoding="utf-8")
            new_hash = self._sha256(content)
            new_version = self._extract_version(content, path.suffix)

            old_hash = self._file_hashes.get(key)
            old_version = self._file_versions.get(key)

            # 触发条件：hash 变化 或 version 递增
            hash_changed = old_hash is not None and new_hash != old_hash
            version_changed = (
                old_version is not None
                and new_version is not None
                and new_version != old_version
            )

            if not (hash_changed or version_changed):
                return None

            # 判断严重级别
            severity = self._assess_severity(content, path, new_version)

            # 找出受影响业务项目
            affected = self._find_affected_projects(path.name)

            # 构建变更事件
            self._event_seq += 1
            event = {
                "event_id": f"EVT-{current_time.strftime('%Y%m%d')}-{self._event_seq:03d}",
                "event_type": "schema_change",
                "changed_files": [{
                    "file": path.name,
                    "old_hash": old_hash or "N/A",
                    "new_hash": new_hash,
                    "old_version": old_version or "N/A",
                    "new_version": new_version or "N/A",
                    "changed_at": current_time.isoformat()
                }],
                "affected_biz_projects": affected,
                "severity": severity.value,
                "timestamp": current_time.isoformat()
            }

            # 更新快照
            self._file_hashes[key] = new_hash
            if new_version:
                self._file_versions[key] = new_version

            return event

        except Exception:
            return None

    def _assess_severity(
        self, content: str, path: Path, new_version: Optional[str]
    ) -> ChangeSeverity:
        """评估变更严重级别"""
        # E2 schema 文件 + 有 breaking 关键字
        if "breaking" in content.lower() or "BREAKING" in content:
            return ChangeSeverity.BREAKING
        # major version 变更
        if new_version and new_version.startswith("2."):
            return ChangeSeverity.CRITICAL
        return ChangeSeverity.INFO

    def _find_affected_projects(self, filename: str) -> List[str]:
        """根据文件名找出受影响业务项目"""
        # E2-schema-finance.json → ["1.2-finance"]
        # E3-glossary-{id}.json → ["1.x-{id}"]
        affected = []
        biz_projects_dir = self.pmo_root / "biz-projects"
        if biz_projects_dir.exists():
            for proj_dir in biz_projects_dir.iterdir():
                if not proj_dir.is_dir():
                    continue
                # 匹配项目 ID 格式
                match = re.match(r"^(\d+\.\d+-.+)$", proj_dir.name)
                if not match:
                    continue
                biz_id = match.group(1)
                # 从文件名提取业务类型
                if filename.startswith("E2-schema-"):
                    biz_type = filename.replace("E2-schema-", "").replace(".json", "")
                    if biz_type in biz_id:
                        affected.append(biz_id)
                elif filename.startswith("E3-glossary-"):
                    biz_type = filename.replace("E3-glossary-", "").replace(".json", "")
                    if biz_type in biz_id:
                        affected.append(biz_id)
        return affected

    # ---------------- 变更事件处理 ----------------
    def _handle_change_event(self, event: Dict[str, Any]):
        """处理变更事件：写日志 + 发 Ping + 记录 ACK"""
        event_id = event["event_id"]

        # 1. 写事件日志
        self._write_event_log(event)

        # 2. 保存待 ACK 状态
        deadline = datetime.now(timezone.utc) + timedelta(days=self.ACK_TIMEOUT_DAYS)
        self._pending_acks[event_id] = {
            "event": event,
            "deadline": deadline.isoformat(),
            "acks": {},   # biz_project_id → ack status
            "sent": datetime.now(timezone.utc).isoformat()
        }

        # 3. 发轻量 Ping（不发完整内容）
        self._send_ping(event)

    def _write_event_log(self, event: Dict[str, Any]):
        """写事件日志到 logs/schema-watcher/change-events-YYYYMMDD.json"""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_file = self.events_dir / f"change-events-{today}.json"
        try:
            events = []
            if log_file.exists():
                try:
                    events = json.loads(log_file.read_text(encoding="utf-8"))
                    if not isinstance(events, list):
                        events = [events]
                except Exception:
                    events = []
            events.append(event)
            log_file.write_text(
                json.dumps(events, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

        # 持久化事件序号
        self._save_event_seq()

    def _send_ping(self, event: Dict[str, Any]):
        """发轻量 Ping 到 pmo.schema.change（Message-Broker）"""
        try:
            # 轻量 payload（不包含完整 diff）
            payload = {
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "changed_files_summary": [
                    f["file"] for f in event["changed_files"]
                ],
                "severity": event["severity"],
                "pmo_instance": "PMO-L1",
                "timestamp": event["timestamp"],
                "affected_biz_projects": event["affected_biz_projects"],
                "pull_url": f"/pmo-api/v1/schema/changes/{event['event_id']}"
            }

            self.broker.publish(
                from_project="pmo-schema-watcher",
                to_project="biz-system",
                topic=self.PMO_SCHEMA_CHANGE_TOPIC,
                msg_type="notification",
                content=payload,
                qos="1",
                layer="pmo"
            )
        except Exception:
            pass

    # ---------------- ACK 管理 ----------------
    def receive_ack(self, event_id: str, biz_project_id: str,
                    status: str, note: str = "") -> bool:
        """业务系统发 ACK，确认已适配"""
        if event_id not in self._pending_acks:
            return False
        self._pending_acks[event_id]["acks"][biz_project_id] = {
            "status": status,  # adapted / in_progress / blocked
            "note": note,
            "received_at": datetime.now(timezone.utc).isoformat()
        }
        return True

    def check_ack_timeouts(self) -> List[Dict[str, Any]]:
        """检查 ACK 超时，返回超时告警列表"""
        alerts = []
        now = datetime.now(timezone.utc)
        for event_id, state in list(self._pending_acks.items()):
            deadline = datetime.fromisoformat(state["deadline"].replace("Z", "+00:00"))
            if now > deadline:
                # 超时：检查是否所有受影响项目都 ACK 了
                affected = state["event"].get("affected_biz_projects", [])
                acked = set(state["acks"].keys())
                missing = [p for p in affected if p not in acked]
                if missing:
                    severity = state["event"].get("severity", "info")
                    is_breaking = severity in (ChangeSeverity.BREAKING.value, ChangeSeverity.CRITICAL.value)
                    alerts.append({
                        "event_id": event_id,
                        "missing_projects": missing,
                        "severity": "escalation" if is_breaking else "warning",
                        "deadline": state["deadline"],
                        "checked_at": now.isoformat()
                    })
                # 从待处理中移除已超时的
                del self._pending_acks[event_id]
        return alerts

    def get_pending_acks(self) -> Dict[str, Any]:
        """获取所有待 ACK 状态"""
        return {
            "pending": [
                {
                    "event_id": eid,
                    "affected": s["event"].get("affected_biz_projects", []),
                    "acked": list(s["acks"].keys()),
                    "deadline": s["deadline"],
                    "severity": s["event"].get("severity", "info")
                }
                for eid, s in self._pending_acks.items()
            ],
            "total": len(self._pending_acks)
        }

    # ---------------- 变更拉取接口（模拟 PMO API） ----------------
    def get_change(self, event_id: str) -> Optional[Dict[str, Any]]:
        """GET /pmo-api/v1/schema/changes/{event_id}"""
        # 从今日事件文件中查找
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_file = self.events_dir / f"change-events-{today}.json"
        if not log_file.exists():
            return None
        try:
            events = json.loads(log_file.read_text(encoding="utf-8"))
            for ev in events:
                if ev.get("event_id") == event_id:
                    # 补充拉取信息
                    ev["pulled_at"] = datetime.now(timezone.utc).isoformat()
                    ev["pull_url"] = f"/pmo-api/v1/schema/changes/{event_id}"
                    ev["ack_url"] = f"/pmo-api/v1/schema/acks/{event_id}"
                    ev["issued_by"] = "PMO-L1"
                    ev["issued_at"] = ev["timestamp"]
                    # info 级 deadline = now + 7d, breaking = now + 3d
                    severity = ev.get("severity", "info")
                    days = 3 if severity in ("breaking", "critical") else 7
                    ev["deadline"] = (
                        datetime.now(timezone.utc) + timedelta(days=days)
                    ).strftime("%Y-%m-%d")
                    return ev
        except Exception:
            pass
        return None

    def get_changes_since(self, since: str, biz_project: str = None) -> Dict[str, Any]:
        """GET /pmo-api/v1/schema/changes?since={timestamp}&biz_project={id}"""
        changes = []
        for log_file in self.events_dir.glob("change-events-*.json"):
            try:
                events = json.loads(log_file.read_text(encoding="utf-8"))
                if not isinstance(events, list):
                    events = [events]
                for ev in events:
                    ev_time = ev.get("timestamp", "")
                    if ev_time >= since:
                        if biz_project is None or biz_project in ev.get("affected_biz_projects", []):
                            changes.append(ev)
            except Exception:
                pass
        return {
            "changes": changes,
            "total": len(changes),
            "page": 1,
            "per_page": 20
        }

    # ---------------- 业务上报入口 ----------------
    def handle_biz_report(self, biz_project_id: str, report_type: str,
                          payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理业务系统上报（metric / exception / data）

        Args:
            biz_project_id: 业务项目 ID
            report_type: metric | exception | data
            payload: 上报内容
        """
        topic_map = {
            "metric": f"biz.{biz_project_id}.metric",
            "exception": f"biz.{biz_project_id}.exception",
            "data": f"biz.{biz_project_id}.data",
        }
        msg_type_map = {
            "metric": "biz_data",
            "exception": "alert",
            "data": "biz_data",
        }
        qos_map = {
            "metric": "1",     # at-least-once
            "exception": "0",  # fire-and-forget
            "data": "2",       # exactly-once
        }

        topic = topic_map.get(report_type)
        msg_type = msg_type_map.get(report_type, "biz_data")
        qos = qos_map.get(report_type, "1")

        if not topic:
            return {"success": False, "error": f"unknown report_type: {report_type}"}

        payload["biz_project_id"] = biz_project_id
        payload["received_at"] = datetime.now(timezone.utc).isoformat()

        try:
            msg = self.broker.publish(
                from_project=biz_project_id,
                to_project="pmo-receiver",
                topic=topic,
                msg_type=msg_type,
                content=payload,
                qos=qos,
                layer="biz"
            )
            return {
                "success": True,
                "msg_id": msg.msg_id,
                "status": msg.status.value,
                "topic": topic,
                "qos": qos
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ---------------- 监控 ----------------
    def get_watcher_status(self) -> Dict[str, Any]:
        """获取 Watcher 状态"""
        return {
            "version": self.PROTOCOL_VERSION,
            "monitored_files": list(self._file_hashes.keys()),
            "pending_ack_events": len(self._pending_acks),
            "event_seq": self._event_seq,
            "events_dir": str(self.events_dir)
        }


# ============================================
# 演示 / 自测入口
# ============================================
if __name__ == "__main__":
    import sys
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print("=== PMO Schema Watcher 演示 (m0.8, DEC-2026-0008) ===\n")

    watcher = SchemaWatcher(PMO_ROOT)

    # 1. 状态
    print("[1] Watcher 状态")
    status = watcher.get_watcher_status()
    print(f"  - version: {status['version']}")
    print(f"  - monitored files: {len(status['monitored_files'])}")
    print(f"  - pending ack events: {status['pending_ack_events']}")
    print()

    # 2. 主动检测变更
    print("[2] 主动检测变更")
    events = watcher.check_for_changes()
    if events:
        for ev in events:
            print(f"  - {ev['event_id']}: {ev['changed_files'][0]['file']} → {ev['severity']}")
    else:
        print("  - 当前无变更")
    print()

    # 3. 业务上报（metric）
    print("[3] 业务系统上报指标 (biz.1.2-finance.metric)")
    r = watcher.handle_biz_report(
        biz_project_id="1.2-finance",
        report_type="metric",
        payload={
            "phase": "P2-develop",
            "metrics": {
                "flow_latency": 120,
                "exception_rate": 0.02,
                "pass_rate": 0.95,
                "rollback_rate": 0.01,
                "token_consumption": 3500
            },
            "period": "5min"
        }
    )
    print(f"  - success: {r.get('success')}, msg_id: {r.get('msg_id')}, topic: {r.get('topic')}")
    print()

    # 4. 业务上报（exception）
    print("[4] 业务系统上报异常 (biz.1.2-finance.exception)")
    r2 = watcher.handle_biz_report(
        biz_project_id="1.2-finance",
        report_type="exception",
        payload={
            "exception_type": "VALIDATION_ERROR",
            "exception_code": "E2001",
            "message": "Schema validation failed for entity: position",
            "severity": "warning",
            "context": {
                "phase": "P2-develop",
                "entity": "position",
                "field": "notional_amount"
            }
        }
    )
    print(f"  - success: {r2.get('success')}, msg_id: {r2.get('msg_id')}, topic: {r2.get('topic')}")
    print()

    # 5. 业务上报（data）
    print("[5] 业务系统上报关键数据 (biz.1.2-finance.data)")
    r3 = watcher.handle_biz_report(
        biz_project_id="1.2-finance",
        report_type="data",
        payload={
            "data_type": "position_snapshot",
            "data_key": "POS-20260619-001",
            "data_hash": "sha256:abc123def456",
            "payload": {"notional": 1000000, "currency": "USD"}
        }
    )
    print(f"  - success: {r3.get('success')}, msg_id: {r3.get('msg_id')}, topic: {r3.get('topic')}")
    print()

    # 6. ACK 超时检查
    print("[6] ACK 超时检查")
    alerts = watcher.check_ack_timeouts()
    print(f"  - 超时告警: {len(alerts)} 项")
    for a in alerts:
        print(f"  - {a['event_id']}: missing {a['missing_projects']}, severity={a['severity']}")
    print()

    # 7. 待 ACK 状态
    print("[7] 待 ACK 状态")
    pending = watcher.get_pending_acks()
    print(f"  - 待 ACK 事件: {pending['total']} 项")
    for p in pending.get("pending", []):
        print(f"  - {p['event_id']}: affected={p['affected']}, acked={p['acked']}, deadline={p['deadline']}")
    print()

    print("=== m0.8 Schema Watcher 演示完成 ===")
