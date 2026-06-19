"""
PMO 运行时规范增量同步器 (norm_pusher.py, m0.9, DEC-2026-0009)
- 监听 PMO 规范目录变更（immutable/ + config/）
- 检测到变更后，通过 Message-Broker 发 Ping 给受影响业务项目
- 业务项目收到 Ping 后主动 Pull 完整变更
- 支持定时全量同步兜底（每天凌晨）
"""
import hashlib
import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


class NormPusher:
    """PMO 运行时规范增量同步器

    监听目标:
    - immutable/0-governance/       → PMO 元规则（0.0.x）
    - immutable/2-biz-specs/        → 业务契约模板
    - config/thresholds.yaml         → 考核阈值
    - config/data-sync.yaml          → 数据同步策略
    - config/biz-meta/              → 业务元数据（E2/E3）

    消息通道:
    - pmo.norm.change    → governance/契约/阈值变更（NormPusher 发）
    - pmo.schema.change  → E2/E3/schema 变更（SchemaWatcher 发）

    同步模式:
    - 实时: 检测到变更立即发 Ping（通过 Message-Broker）
    - 定时: 每 24 小时全量比对一次（兜底）
    """

    PROTOCOL_VERSION = "0.9.0"
    PMO_NORM_CHANGE_TOPIC = "pmo.norm.change"

    # 变更检测间隔（秒）
    CHECK_INTERVAL = 60

    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.logs_dir = self.pmo_root / "logs" / "norm-pusher"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # 文件 hash 快照
        self._snapshots: Dict[str, str] = {}

        # 事件序号
        self._event_seq = 0
        self._load_event_seq()

        # 事件日志（内存）
        self._events: List[Dict[str, Any]] = []

        # Message-Broker（lazy init）
        self._broker = None

        # Watchdog 线程
        self._watchdog_thread: Optional[threading.Thread] = None
        self._watchdog_stop = threading.Event()

        # 初始化快照
        self._init_snapshots()

    # ---------------- Broker 懒加载 ----------------
    @property
    def broker(self):
        if self._broker is None:
            from protocol.message_broker import MessageBroker
            self._broker = MessageBroker(str(self.pmo_root))
        return self._broker

    # ---------------- 快照初始化 ----------------
    def _init_snapshots(self):
        """初始化所有监听目录的 hash 快照"""
        watch_paths = [
            self.pmo_root / "immutable" / "0-governance",
            self.pmo_root / "immutable" / "2-biz-specs",
            self.pmo_root / "config",
        ]
        for dir_path in watch_paths:
            if dir_path.exists():
                for f in dir_path.rglob("*"):
                    if f.is_file():
                        self._capture_snapshot(f)

    def _capture_snapshot(self, path: Path):
        key = str(path.relative_to(self.pmo_root))
        try:
            content = path.read_text(encoding="utf-8")
            self._snapshots[key] = self._sha256(content)
        except Exception:
            pass

    def _sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    # ---------------- 事件序号持久化 ----------------
    def _load_event_seq(self):
        seq_file = self.logs_dir / ".event_seq"
        try:
            if seq_file.exists():
                self._event_seq = int(seq_file.read_text().strip())
        except Exception:
            self._event_seq = 0

    def _save_event_seq(self):
        seq_file = self.logs_dir / ".event_seq"
        try:
            seq_file.write_text(str(self._event_seq))
        except Exception:
            pass

    # ---------------- 变更检测 ----------------
    def detect_changes(self) -> List[Dict[str, Any]]:
        """主动检测规范目录变更，返回变更事件列表"""
        events = []
        current_time = datetime.now(timezone.utc)

        # immutable/0-governance/
        gov_dir = self.pmo_root / "immutable" / "0-governance"
        if gov_dir.exists():
            for f in gov_dir.glob("0.0.*.md"):
                ev = self._check_file(f, current_time, "governance")
                if ev:
                    events.append(ev)

        # immutable/2-biz-specs/
        specs_dir = self.pmo_root / "immutable" / "2-biz-specs"
        if specs_dir.exists():
            for f in specs_dir.glob("*.md"):
                ev = self._check_file(f, current_time, "biz_specs")
                if ev:
                    events.append(ev)

        # config/thresholds.yaml
        thresh_file = self.pmo_root / "config" / "thresholds.yaml"
        if thresh_file.exists():
            ev = self._check_file(thresh_file, current_time, "thresholds")
            if ev:
                events.append(ev)

        # config/data-sync.yaml
        data_sync_file = self.pmo_root / "config" / "data-sync.yaml"
        if data_sync_file.exists():
            ev = self._check_file(data_sync_file, current_time, "data_sync")
            if ev:
                events.append(ev)

        # config/biz-meta/E2/E3
        biz_meta_dir = self.pmo_root / "config" / "biz-meta"
        if biz_meta_dir.exists():
            for f in biz_meta_dir.rglob("E2-*.json"):
                ev = self._check_file(f, current_time, "e2_schema")
                if ev:
                    events.append(ev)
            for f in biz_meta_dir.rglob("E3-*.json"):
                ev = self._check_file(f, current_time, "e3_glossary")
                if ev:
                    events.append(ev)

        # 处理每个事件
        for ev in events:
            self._handle_change_event(ev)

        return events

    def _check_file(self, path: Path, current_time: datetime,
                    norm_type: str) -> Optional[Dict[str, Any]]:
        key = str(path.relative_to(self.pmo_root))
        try:
            content = path.read_text(encoding="utf-8")
            new_hash = self._sha256(content)

            old_hash = self._snapshots.get(key)
            if old_hash is None:
                self._snapshots[key] = new_hash
                return None
            if new_hash == old_hash:
                return None

            # 有变更
            self._event_seq += 1
            event = {
                "event_id": f"NORM-EVT-{current_time.strftime('%Y%m%d')}-{self._event_seq:03d}",
                "event_type": "norm_change",
                "norm_type": norm_type,
                "changed_file": key,
                "old_hash": old_hash,
                "new_hash": new_hash,
                "changed_at": current_time.isoformat(),
                "affected_biz_projects": self._find_affected_projects(key),
                "severity": self._assess_severity(norm_type, key),
                "timestamp": current_time.isoformat(),
                "pull_url": f"/pmo-api/v1/norms/changes/{norm_type}/{path.name}",
                "pull_content_url": f"/pmo-api/v1/norms/files/{key}"
            }

            self._snapshots[key] = new_hash
            self._save_event_seq()
            return event

        except Exception:
            return None

    def _assess_severity(self, norm_type: str, key: str) -> str:
        if norm_type == "governance":
            return "critical"
        elif norm_type in ("thresholds", "biz_specs", "data_sync"):
            return "breaking"
        else:
            return "info"

    def _find_affected_projects(self, changed_file: str) -> List[str]:
        """找出受变更影响的所有 active 业务项目"""
        affected = []
        biz_projects_dir = self.pmo_root / "biz-projects"
        if not biz_projects_dir.exists():
            return affected

        for proj_dir in biz_projects_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            reg_file = proj_dir / "register.yaml"
            if not reg_file.exists():
                continue
            try:
                data = yaml_read(reg_file)
                state = data.get("pmo_supervision", {}).get("state", "")
                if state != "active":
                    continue
            except Exception:
                continue
            affected.append(proj_dir.name)
        return sorted(affected)

    # ---------------- 变更事件处理 ----------------
    def _handle_change_event(self, event: Dict[str, Any]):
        """处理变更事件：写日志 + 发 Ping"""
        self._write_event_log(event)
        self._events.append(event)
        self._send_ping(event)

    def _write_event_log(self, event: Dict[str, Any]):
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_file = self.logs_dir / f"norm-change-events-{today}.json"
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

    def _send_ping(self, event: Dict[str, Any]):
        """发轻量 Ping 到 pmo.norm.change（通过 Message-Broker）"""
        try:
            payload = {
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "norm_type": event["norm_type"],
                "changed_file": event["changed_file"],
                "severity": event["severity"],
                "pmo_instance": "PMO-L1",
                "timestamp": event["timestamp"],
                "affected_biz_projects": event["affected_biz_projects"],
                "pull_url": event["pull_url"],
                "pull_content_url": event["pull_content_url"],
                "protocol_version": self.PROTOCOL_VERSION
            }

            self.broker.publish(
                from_project="pmo-norm-pusher",
                to_project="biz-system",
                topic=self.PMO_NORM_CHANGE_TOPIC,
                msg_type="notification",
                content=payload,
                qos="1",
                layer="pmo"
            )
        except Exception:
            pass

    # ---------------- Pull 接口 ----------------

    def get_norm_change(self, norm_type: str, filename: str) -> Optional[Dict[str, Any]]:
        """GET /pmo-api/v1/norms/changes/{norm_type}/{filename}"""
        type_to_dir = {
            "governance": "immutable/0-governance",
            "biz_specs": "immutable/2-biz-specs",
            "thresholds": "config",
            "data_sync": "config",
            "e2_schema": "config/biz-meta",
            "e3_glossary": "config/biz-meta",
        }
        base_dir = type_to_dir.get(norm_type, "")
        file_path = self.pmo_root / base_dir / filename

        if not file_path.exists():
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
            return {
                "norm_type": norm_type,
                "filename": filename,
                "content": content,
                "hash": self._sha256(content),
                "pulled_at": datetime.now(timezone.utc).isoformat(),
                "protocol_version": self.PROTOCOL_VERSION
            }
        except Exception:
            return None

    def get_norm_file(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """GET /pmo-api/v1/norms/files/{relative_path}"""
        file_path = self.pmo_root / relative_path
        if not file_path.exists():
            return None
        try:
            content = file_path.read_text(encoding="utf-8")
            return {
                "path": relative_path,
                "content": content,
                "hash": self._sha256(content),
                "pulled_at": datetime.now(timezone.utc).isoformat(),
                "protocol_version": self.PROTOCOL_VERSION
            }
        except Exception:
            return None

    def get_changes_since(self, since: str) -> List[Dict[str, Any]]:
        """GET /pmo-api/v1/norms/changes?since={timestamp}"""
        changes = []
        for log_file in self.logs_dir.glob("norm-change-events-*.json"):
            try:
                events = json.loads(log_file.read_text(encoding="utf-8"))
                if not isinstance(events, list):
                    events = [events]
                for ev in events:
                    if ev.get("timestamp", "") >= since:
                        changes.append(ev)
            except Exception:
                pass
        return sorted(changes, key=lambda x: x.get("timestamp", ""))

    # ---------------- 定时全量同步 ----------------

    def daily_full_sync(self) -> Dict[str, Any]:
        """每天凌晨定时全量同步：比对所有规范，对未同步的业务项目补发"""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        sync_results = {}

        current_hashes = self._recompute_hashes()
        new_changes = []

        for key, new_hash in current_hashes.items():
            old_hash = self._snapshots.get(key)
            if old_hash is None or old_hash != new_hash:
                file_path = self.pmo_root / key
                norm_type = self._classify_file(key)
                new_changes.append({
                    "changed_file": key,
                    "new_hash": new_hash,
                    "old_hash": old_hash,
                    "norm_type": norm_type
                })

        active_projects = self._get_active_biz_projects()
        for proj_id in active_projects:
            synced_at = self._get_project_sync_time(proj_id)
            unsynced = [c for c in new_changes
                        if not synced_at or c["new_hash"] != synced_at.get(c["changed_file"])]
            if unsynced:
                self._notify_project_sync(proj_id, unsynced)
                sync_results[proj_id] = {"synced": len(unsynced), "changes": unsynced}

        log_file = self.logs_dir / f"daily-full-sync-{today}.json"
        log_file.write_text(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_projects": active_projects,
            "new_changes_found": len(new_changes),
            "sync_results": sync_results
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "date": today,
            "active_projects": len(active_projects),
            "new_changes": len(new_changes),
            "sync_results": sync_results
        }

    def _recompute_hashes(self) -> Dict[str, str]:
        """重新计算所有规范文件的 hash"""
        hashes = {}
        for dir_name in ["immutable/0-governance", "immutable/2-biz-specs", "config"]:
            d = self.pmo_root / dir_name
            if d.exists():
                for f in d.rglob("*"):
                    if f.is_file():
                        try:
                            key = str(f.relative_to(self.pmo_root))
                            content = f.read_text(encoding="utf-8")
                            hashes[key] = self._sha256(content)
                        except Exception:
                            pass
        return hashes

    def _classify_file(self, key: str) -> str:
        if key.startswith("immutable/0-governance"):
            return "governance"
        elif key.startswith("immutable/2-biz-specs"):
            return "biz_specs"
        elif "thresholds.yaml" in key:
            return "thresholds"
        elif "data-sync.yaml" in key:
            return "data_sync"
        elif "E2-" in key:
            return "e2_schema"
        elif "E3-" in key:
            return "e3_glossary"
        return "unknown"

    def _get_active_biz_projects(self) -> List[str]:
        active = []
        biz_dir = self.pmo_root / "biz-projects"
        if not biz_dir.exists():
            return active
        for proj_dir in biz_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            reg_file = proj_dir / "register.yaml"
            if not reg_file.exists():
                continue
            try:
                data = yaml_read(reg_file)
                if data.get("pmo_supervision", {}).get("state") == "active":
                    active.append(proj_dir.name)
            except Exception:
                pass
        return sorted(active)

    def _get_project_sync_time(self, proj_id: str) -> Dict[str, str]:
        sync_file = self.pmo_root / "biz-projects" / proj_id / "reports" / "sync-metadata.json"
        if not sync_file.exists():
            return {}
        try:
            return json.loads(sync_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _notify_project_sync(self, proj_id: str, changes: List[Dict]):
        try:
            self.broker.publish(
                from_project="pmo-norm-pusher",
                to_project=proj_id,
                topic=self.PMO_NORM_CHANGE_TOPIC,
                msg_type="notification",
                content={
                    "event_type": "norm_full_sync_reminder",
                    "proj_id": proj_id,
                    "changes_count": len(changes),
                    "changed_files": [c["changed_file"] for c in changes],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "pull_url": "/pmo-api/v1/norms/full-sync"
                },
                qos="1",
                layer="pmo"
            )
        except Exception:
            pass

    # ---------------- Watchdog 线程 ----------------

    def start_watching(self, interval: int = None):
        """启动后台监听线程（每 interval 秒检测一次）"""
        if interval is None:
            interval = self.CHECK_INTERVAL
        self._watchdog_stop.clear()
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            args=(interval,),
            daemon=True
        )
        self._watchdog_thread.start()

    def stop_watching(self):
        """停止后台监听线程"""
        self._watchdog_stop.set()
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=5)
            self._watchdog_thread = None

    def _watchdog_loop(self, interval: int):
        while not self._watchdog_stop.is_set():
            events = self.detect_changes()
            if events:
                print(f"[NormPusher] 检测到 {len(events)} 个变更事件")
            self._watchdog_stop.wait(interval)

    # ---------------- 状态查询 ----------------

    def get_pusher_status(self) -> Dict[str, Any]:
        return {
            "version": self.PROTOCOL_VERSION,
            "monitored_files": len(self._snapshots),
            "pending_events": len(self._events),
            "event_seq": self._event_seq,
            "watching": self._watchdog_thread is not None and self._watchdog_thread.is_alive(),
            "logs_dir": str(self.logs_dir)
        }


# ============================================
# 辅助
# ============================================
def yaml_read(path: Path) -> Dict[str, Any]:
    import yaml as _yaml
    with open(path, encoding="utf-8") as f:
        return _yaml.safe_load(f) or {}


# ============================================
# 演示 / 自测入口
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("=== PMO NormPusher 演示 (m0.9, DEC-2026-0009) ===\n")

    pusher = NormPusher(PMO_ROOT)

    print("[1] NormPusher 状态")
    status = pusher.get_pusher_status()
    print(f"  - version: {status['version']}")
    print(f"  - monitored_files: {status['monitored_files']}")
    print(f"  - event_seq: {status['event_seq']}")
    print()

    print("[2] 主动检测变更")
    events = pusher.detect_changes()
    if events:
        for ev in events:
            print(f"  - {ev['event_id']}: {ev['changed_file']} ({ev['norm_type']})")
    else:
        print("  - 当前无变更")
    print()

    print("[3] Pull 接口演示（thresholds.yaml）")
    content = pusher.get_norm_file("config/thresholds.yaml")
    if content:
        print(f"  - path: {content['path']}")
        print(f"  - hash: {content['hash']}")
        print(f"  - content length: {len(content['content'])} chars")
    print()

    print("[4] Active 业务项目")
    active = pusher._get_active_biz_projects()
    print(f"  - count: {len(active)}")
    for pid in active:
        print(f"  - {pid}")
    print()

    print("=== NormPusher 演示完成 ===")
