"""
biz_version_store.py — F5 业务版本管理 (m2.2, DEC-2026-0006)

Git tag/release + semver 业务版本追踪。

存储位置: config/biz-meta/<biz_id>-versions.json
"""

import json
import os
import re
from datetime import datetime
from typing import Optional


PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

TAG_PATTERN = re.compile(
    r"^biz\.([a-zA-Z0-9_.-]+)\.v(\d+)\.(\d+)\.(\d+)$"
)
TAG_PATTERN_RC = re.compile(
    r"^biz\.([a-zA-Z0-9_.-]+)\.v(\d+)\.(\d+)\.(\d+)-rc\.(\d+)$"
)


class VersionRecord:
    def __init__(self, tag: str, version: str, phase: str,
                 commit: str, date: str, notes: str = ""):
        self.tag = tag
        self.version = version
        self.phase = phase
        self.commit = commit
        self.date = date
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "version": self.version,
            "phase": self.phase,
            "commit": self.commit,
            "date": self.date,
            "notes": self.notes,
        }

    def __repr__(self) -> str:
        return f"<VersionRecord {self.tag} {self.version}>"


class BizVersionStore:
    """
    业务项目版本管理:
    - 管理 biz.<id>.v<MAJOR>.<MINOR>.<PATCH> 格式的 Git tag
    - 存储在 config/biz-meta/<biz_id>-versions.json
    - semver 规则: MAJOR 破坏性变更 / MINOR 新增 / PATCH 修复
    """

    def __init__(self, biz_id: str, pmo_root: str = PMO_ROOT):
        self.biz_id = biz_id
        self.pmo_root = pmo_root
        self.store_dir = os.path.join(pmo_root, "config", "biz-meta")
        self.store_file = os.path.join(
            self.store_dir, f"{biz_id}-versions.json")
        self._ensure_store_dir()
        self._versions: list[VersionRecord] = self._load()

    def _ensure_store_dir(self):
        if not os.path.exists(self.store_dir):
            os.makedirs(self.store_dir, exist_ok=True)

    def _load(self) -> list[VersionRecord]:
        if not os.path.exists(self.store_file):
            return []
        try:
            with open(self.store_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [VersionRecord(**r) for r in data]
        except (json.JSONDecodeError, TypeError):
            return []

    def _save(self):
        with open(self.store_file, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in self._versions],
                      f, ensure_ascii=False, indent=2)

    def parse_tag(self, tag: str) -> Optional[dict]:
        """
        解析 tag 格式: biz.<biz_id>.v<MAJOR>.<MINOR>.<PATCH>[-rc.N]
        返回 version dict 或 None
        """
        m = TAG_PATTERN.match(tag)
        if m:
            return {
                "biz_id": m.group(1),
                "major": int(m.group(2)),
                "minor": int(m.group(3)),
                "patch": int(m.group(4)),
                "prerelease": None,
                "full": tag,
            }
        m2 = TAG_PATTERN_RC.match(tag)
        if m2:
            return {
                "biz_id": m2.group(1),
                "major": int(m2.group(2)),
                "minor": int(m2.group(3)),
                "patch": int(m2.group(4)),
                "prerelease": f"rc.{m2.group(5)}",
                "full": tag,
            }
        return None

    def release(self, phase: str, notes: str = "",
                commit: str = "HEAD") -> VersionRecord:
        """
        发布一个新版本:
        - 首次: v1.0.0
        - PATCH: 上一个 PATCH+1
        - MINOR: 上一个 MINOR+1, PATCH=0
        - MAJOR: 上一个 MAJOR+1, MINOR=0, PATCH=0

        phase: "requirement" | "development" | "test" | "operations" | "evaluation"
        """
        if not self._versions:
            major, minor, patch = 1, 0, 0
        else:
            last = self._versions[-1]
            parsed = self.parse_tag(last.tag)
            if parsed is None:
                major, minor, patch = 1, 0, 0
            else:
                major = parsed["major"]
                minor = parsed["minor"]
                patch = parsed["patch"]
            patch += 1
        tag = f"biz.{self.biz_id}.v{major}.{minor}.{patch}"

        date = datetime.now().strftime("%Y-%m-%d")
        record = VersionRecord(
            tag=tag,
            version=f"v{major}.{minor}.{patch}",
            phase=phase,
            commit=commit,
            date=date,
            notes=notes,
        )
        self._versions.append(record)
        self._save()
        return record

    def get_latest(self) -> Optional[VersionRecord]:
        return self._versions[-1] if self._versions else None

    def get_history(self, limit: int = 10) -> list[VersionRecord]:
        return self._versions[-limit:]

    def compare_versions(self, v1: str, v2: str) -> int:
        """
        比较两个 semver 版本:
        返回 -1 (v1 < v2) / 0 (=) / 1 (v1 > v2)
        """
        def parse(s: str) -> tuple[int, int, int]:
            s = s.lstrip("v")
            parts = s.split(".")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        p1, p2 = parse(v1), parse(v2)
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
        return 0

    def next_major(self, notes: str = "") -> VersionRecord:
        """主动升级 MAJOR (破坏性变更): (X+1).0.0"""
        if not self._versions:
            major, minor, patch = 1, 0, 0
        else:
            last = self._versions[-1]
            parsed = self.parse_tag(last.tag)
            if parsed is None:
                major, minor, patch = 1, 0, 0
            else:
                major = parsed["major"] + 1
                minor = 0
                patch = 0
        tag = f"biz.{self.biz_id}.v{major}.{minor}.{patch}"
        date = datetime.now().strftime("%Y-%m-%d")
        record = VersionRecord(
            tag=tag, version=f"v{major}.{minor}.{patch}", phase="evaluation",
            commit="HEAD", date=date, notes=notes)
        self._versions.append(record)
        self._save()
        return record

    def next_minor(self, notes: str = "") -> VersionRecord:
        """主动升级 MINOR (新增功能): vX.(Y+1).0"""
        if not self._versions:
            major, minor, patch = 1, 0, 0
        else:
            last = self._versions[-1]
            parsed = self.parse_tag(last.tag)
            if parsed is None:
                major, minor, patch = 1, 0, 0
            else:
                major = parsed["major"]
                minor = parsed["minor"] + 1
                patch = 0
        tag = f"biz.{self.biz_id}.v{major}.{minor}.{patch}"
        date = datetime.now().strftime("%Y-%m-%d")
        record = VersionRecord(
            tag=tag, version=f"v{major}.{minor}.{patch}", phase="evaluation",
            commit="HEAD", date=date, notes=notes)
        self._versions.append(record)
        self._save()
        return record

    def dump(self) -> dict:
        return {
            "biz_id": self.biz_id,
            "store_file": self.store_file,
            "versions": [r.to_dict() for r in self._versions],
            "count": len(self._versions),
        }


if __name__ == "__main__":
    print("=== F5 业务版本管理演示 ===\n")

    # 演示 1.2-finance semver 演进
    print("--- 1.2-finance ---")
    store = BizVersionStore("1.2-finance")
    print(f"BizID: {store.biz_id}")
    print(f"Store: {store.store_file}")

    # === 演示正确的 semver 版本演进 ===
    # 1. 新业务项目: 首个 release
    print("\n--- semver 演进演示 ---")
    store2 = BizVersionStore("1.1-pmo-self")
    r1 = store2.release("requirement", "初始化需求文档")
    print(f"  v1.0.0 [release]: {r1.tag}")

    r2 = store2.release("development", "设计 + 实施文档")
    print(f"  v1.0.1 [release]: {r2.tag}")

    # 2. 新增功能 -> MINOR 升级
    r3 = store2.next_minor("新增 risk_metric 实体")
    print(f"  v1.1.0 [next_minor]: {r3.tag}")

    # 3. 破坏性变更 -> MAJOR 升级
    r4 = store2.next_major("E2 schema 破坏性重构")
    print(f"  v2.0.0 [next_major]: {r4.tag}")

    print(f"\n  semver compare v1.0.0 vs v1.1.0: {store2.compare_versions('v1.0.0', 'v1.1.0')}")
    print(f"  semver compare v1.1.0 vs v2.0.0: {store2.compare_versions('v1.1.0', 'v2.0.0')}")

    # === 1.1-pmo-self ===
    print("\n--- 1.1-pmo-self ---")
    store3 = BizVersionStore("1.1-pmo-self")
    r5 = store3.release("evaluation", "PMO 自建初始发布")
    print(f"  v1.0.0 [release]: {r5.tag}")

    print(f"\n=== 版本历史 ===")
    for v in store2.get_history():
        print(f"  {v.tag} | {v.version} | {v.phase} | {v.date}")
    for v in store3.get_history():
        print(f"  {v.tag} | {v.version} | {v.phase} | {v.date}")
    print("\n✅ F5 业务版本管理 演示完成")
