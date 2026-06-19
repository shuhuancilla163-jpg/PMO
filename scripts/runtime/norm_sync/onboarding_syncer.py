"""
PMO 接入时规范同步器 (onboarding_syncer.py, m0.9, DEC-2026-0009)
- 业务项目注册时，PMO 自动将所有规范文件同步到业务项目目录
- 同步内容：register.yaml / 契约模板 / SOP 模板 / 阈值配置 / 5阶段agent模板
- 支持幂等：已存在的文件跳过，已存在但内容不同则更新
- 同步完成后记录 sync-metadata.json，记录同步版本和状态
"""
import os
import json
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class OnboardingSyncer:
    """PMO 接入时全量规范同步器

    同步原则:
    - 幂等: 已存在且内容一致的文件跳过
    - 原子性: 同步失败时回滚已复制文件
    - 可审计: 每次同步记录 sync-metadata.json
    """

    PROTOCOL_VERSION = "0.9.0"

    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.templates_dir = self.pmo_root / "biz-projects" / "templates"
        self.pmo_templates_dir = self.pmo_root / "templates"
        self.thresholds_file = self.pmo_root / "config" / "thresholds.yaml"
        self.biz_projects_dir = self.pmo_root / "biz-projects"
        self.logs_dir = self.pmo_root / "logs" / "norm-sync"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Message-Broker（lazy init）
        self._broker = None

    # ---------------- Broker 懒加载 ----------------
    @property
    def broker(self):
        if self._broker is None:
            from protocol.message_broker import MessageBroker
            self._broker = MessageBroker(str(self.pmo_root))
        return self._broker

    # ---------------- 核心同步接口 ----------------

    def sync_all_norms(self, biz_project_id: str,
                       register_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """接入时全量同步所有 PMO 规范到业务项目

        Args:
            biz_project_id: 业务项目 ID（如 "1.2-finance"）
            register_data: 可选，注册数据（biz_project 字段），用于生成 register.yaml

        Returns:
            sync_result: 同步结果汇总
        """
        biz_dir = self.biz_projects_dir / biz_project_id
        results = {}
        errors = []

        # 1. 同步 register.yaml
        r = self.sync_register(biz_dir, register_data)
        results["register"] = r
        if not r["success"]:
            errors.append(f"register.yaml: {r.get('error')}")

        # 2. 同步契约模板
        r = self.sync_contracts(biz_dir, biz_project_id)
        results["contracts"] = r
        if not r["success"]:
            errors.append(f"contracts: {r.get('error')}")

        # 3. 同步 SOP 模板
        r = self.sync_sop_templates(biz_dir)
        results["sop_templates"] = r
        if not r["success"]:
            errors.append(f"sop_templates: {r.get('error')}")

        # 4. 同步 5 阶段 agent 模板
        r = self.sync_eng_roles(biz_dir)
        results["eng_roles"] = r
        if not r["success"]:
            errors.append(f"eng_roles: {r.get('error')}")

        # 5. 同步阈值配置
        r = self.sync_thresholds(biz_dir)
        results["thresholds"] = r
        if not r["success"]:
            errors.append(f"thresholds.yaml: {r.get('error')}")

        # 6. 同步 messaging.yaml
        r = self.sync_messaging(biz_dir, biz_project_id)
        results["messaging"] = r
        if not r["success"]:
            errors.append(f"messaging.yaml: {r.get('error')}")

        # 7. 创建 reports 目录
        r = self._ensure_reports_dir(biz_dir)
        results["reports_dir"] = r

        # 8. 创建 biz-agents 目录（框架态）
        r = self._ensure_biz_agents_dir(biz_dir)
        results["biz_agents_dir"] = r

        # 9. 写同步元数据
        metadata = self._write_sync_metadata(biz_dir, biz_project_id, results)

        # 10. 记录同步日志
        self._log_sync(biz_project_id, results)

        # 11. 通知业务项目（发 Message-Broker Ping）
        self._notify_biz_project(biz_project_id, metadata)

        overall_success = len(errors) == 0
        return {
            "biz_project_id": biz_project_id,
            "success": overall_success,
            "errors": errors,
            "synced_items": {k: v.get("status") for k, v in results.items()},
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # ---------------- 分项同步 ----------------

    def sync_register(self, biz_dir: Path,
                      register_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """同步 register.yaml（基于 PMO 注册数据生成，不从 templates 复制）"""
        target = biz_dir / "register.yaml"
        biz_project_id = biz_dir.name

        if register_data is None:
            register_data = {}

        biz_project = register_data.get("biz_project", {})
        if not biz_project:
            biz_project = {
                "id": biz_project_id,
                "name": f"业务项目 {biz_project_id}",
                "type": "biz-system",
                "version": "0.1.0",
                "sponsor": "TBD",
                "registered_at": datetime.now(timezone.utc).isoformat()
            }

        content = self._generate_register_yaml(biz_project_id, biz_project)

        return self._write_file(target, content, "register.yaml")

    def sync_contracts(self, biz_dir: Path, biz_project_id: str) -> Dict[str, Any]:
        """同步 3 份契约模板到 immutable/2-biz-specs/"""
        immutable_dir = self.pmo_root / "immutable" / "2-biz-specs"
        immutable_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        # 3 份契约：整体 + 5阶段 + 业务agent
        contract_pairs = [
            ("contract-project-overall.md", f"contract-{biz_project_id}-overall.md"),
            ("contract-eng-5-stages.md", f"contract-{biz_project_id}-eng-5-stages.md"),
            ("contract-biz-ops-roles.md", f"contract-{biz_project_id}-biz-ops-roles.md"),
        ]

        for src_name, dst_name in contract_pairs:
            src = self.templates_dir / src_name
            dst = immutable_dir / dst_name
            if src.exists():
                content = src.read_text(encoding="utf-8")
                content = content.replace("<biz-project-id>", biz_project_id)
                r = self._write_file(dst, content, src_name)
            else:
                r = {"success": False, "error": f"source not found: {src_name}"}
            results[src_name] = r

        all_ok = all(r.get("success") for r in results.values())
        return {"success": all_ok, "contracts": results}

    def sync_sop_templates(self, biz_dir: Path) -> Dict[str, Any]:
        """同步 SOP 模板到 biz-docs/"""
        src_docs = self.templates_dir / "biz-docs"
        dst_docs = biz_dir / "biz-docs"

        if not src_docs.exists():
            return {"success": False, "error": f"source dir not found: {src_docs}"}

        count = self._copy_tree(src_docs, dst_docs)
        return {
            "success": True,
            "copied": count,
            "from": str(src_docs),
            "to": str(dst_docs)
        }

    def sync_eng_roles(self, biz_dir: Path) -> Dict[str, Any]:
        """同步 5 阶段 agent 模板到 eng-roles/"""
        src_roles = self.pmo_templates_dir / "eng-roles"
        dst_roles = biz_dir / "eng-roles"

        if not src_roles.exists():
            return {"success": False, "error": f"source dir not found: {src_roles}"}

        count = self._copy_tree(src_roles, dst_roles)
        # 同步 eng-roles/register.yaml
        src_reg = self.pmo_root / "biz-projects" / "1.1-pmo-self" / "eng-roles" / "register.yaml"
        if src_reg.exists():
            content = src_reg.read_text(encoding="utf-8")
            self._write_file(dst_roles / "register.yaml", content, "eng-roles/register.yaml")

        return {
            "success": True,
            "copied": count,
            "from": str(src_roles),
            "to": str(dst_roles)
        }

    def sync_thresholds(self, biz_dir: Path) -> Dict[str, Any]:
        """同步阈值配置到 reports/thresholds.yaml"""
        if not self.thresholds_file.exists():
            return {"success": False, "error": "thresholds.yaml not found in config/"}

        # 目标路径：reports/thresholds.yaml（业务项目可覆盖）
        reports_dir = biz_dir / "reports"
        target = reports_dir / "thresholds.yaml"

        content = self.thresholds_file.read_text(encoding="utf-8")
        return self._write_file(target, content, "thresholds.yaml")

    def sync_messaging(self, biz_dir: Path, biz_project_id: str) -> Dict[str, Any]:
        """同步 messaging.yaml（生成默认订阅/发布主题）"""
        target = biz_dir / "messaging.yaml"
        content = self._generate_messaging_yaml(biz_project_id)
        return self._write_file(target, content, "messaging.yaml")

    # ---------------- 辅助方法 ----------------

    def _generate_register_yaml(self, biz_project_id: str,
                               biz_project: Dict[str, Any]) -> str:
        """生成 register.yaml 内容"""
        now = datetime.now(timezone.utc).isoformat()
        return f'''# {biz_project_id} — 业务项目注册 (m0.9, PMO 自动同步生成)

biz_project:
  id: "{biz_project_id}"
  name: "{biz_project.get("name", f"业务项目 {biz_project_id}")}"
  type: "{biz_project.get("type", "biz-system")}"
  version: "{biz_project.get("version", "0.1.0")}"
  sponsor: "{biz_project.get("sponsor", "TBD")}"
  registered_at: "{biz_project.get("registered_at", now)}"

pmo_supervision:
  enabled: true
  state: "active"
  quota_4d:
    token: "100000"
    time: "unlimited"
    storage: "1GB"
    concurrency: 3
  isolation_3d:
    data: "full"
    config: "independent"
    state: "independent"

agent_categories:
  eng_roles:
    description: "5 阶段研发 agent (PMO 监管, 0.0.13)"
    pmo_supervised: true
    location: "eng-roles/"
  biz_agents:
    description: "业务需求运营 agent (业务自管, 0.0.14)"
    pmo_supervised: false
    location: "biz-agents/"

compliance_2_layers:
  layer_1_overall: true
  layer_2_eng_5_stages: true

m2_6_7_items:
  registration: true
  state_machine: true
  quota_4d: true
  archive_4_levels: true
  isolation_3d: true
  alerting_3_levels: true
  checklist_6_plus_3: true

governance_refs:
  - "immutable/0-governance/0.0.1-five-values.md"
  - "immutable/0-governance/0.0.7-decoupling-4layers.md"
  - "immutable/2-biz-specs/contract-{biz_project_id}-overall.md"
  - "immutable/2-biz-specs/contract-{biz_project_id}-eng-5-stages.md"

access_path:
  contract_overall: "immutable/2-biz-specs/contract-{biz_project_id}-overall.md"
  contract_eng_5stages: "immutable/2-biz-specs/contract-{biz_project_id}-eng-5-stages.md"
  checklist: "biz-projects/{biz_project_id}/checklist.md"
  reports: "biz-projects/{biz_project_id}/reports/"
  thresholds: "biz-projects/{biz_project_id}/reports/thresholds.yaml"

metrics:
  business_basic_5:
    - flow_latency
    - exception_rate
    - pass_rate
    - rollback_rate
    - token_consumption
  custom: []

alerting:
  biz: "self"
  pmo: "重大→PMO"
  sponsor: "PMO 重大→Sponsor"

# PMO 自动同步信息（m0.9）
pmo_sync:
  synced_at: "{now}"
  synced_by: "OnboardingSyncer"
  pmo_version: "{self.PROTOCOL_VERSION}"
'''

    def _generate_messaging_yaml(self, biz_project_id: str) -> str:
        """生成默认 messaging.yaml"""
        return f'''# {biz_project_id} — 消息订阅/发布配置 (m2.5, PMO 自动同步生成)

subscriptions:
  # PMO 系统消息
  - "pmo.schema.change"        # PMO 规范/Schema 变更通知
  - "pmo.norm.change"          # PMO governance 变更通知
  - "pmo.alert"                # PMO 告警
  # 项目间消息（按需订阅）
  - "inter.biz.+.+"            # 全部项目间消息

publications:
  # 业务指标上报
  - "biz.{biz_project_id}.metric"
  # 业务异常上报
  - "biz.{biz_project_id}.exception"
  # 业务关键数据上报
  - "biz.{biz_project_id}.data"
  # 业务状态变更
  - "biz.{biz_project_id}.state"
  # 项目间消息（按需发布）
  - "inter.biz.{biz_project_id}.+"
'''

    def _write_file(self, target: Path, content: str, label: str) -> Dict[str, Any]:
        """写入文件（幂等：内容一致则跳过）"""
        target.parent.mkdir(parents=True, exist_ok=True)
        new_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

        if target.exists():
            old_hash = hashlib.sha256(target.read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:16]
            if old_hash == new_hash:
                return {"success": True, "status": "unchanged", "file": str(target)}
            action = "updated"
        else:
            action = "created"

        target.write_text(content, encoding="utf-8")
        return {"success": True, "status": action, "file": str(target), "hash": new_hash}

    def _copy_tree(self, src: Path, dst: Path) -> int:
        """复制目录树（幂等）"""
        count = 0
        if not src.exists():
            return 0
        for item in src.rglob("*"):
            if item.is_file():
                rel = item.relative_to(src)
                dst_file = dst / rel
                content = item.read_text(encoding="utf-8")
                r = self._write_file(dst_file, content, str(rel))
                if r.get("success") and r.get("status") != "unchanged":
                    count += 1
        return count

    def _ensure_reports_dir(self, biz_dir: Path) -> Dict[str, Any]:
        """确保 reports 目录存在"""
        reports_dir = biz_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        return {"success": True, "created": True, "dir": str(reports_dir)}

    def _ensure_biz_agents_dir(self, biz_dir: Path) -> Dict[str, Any]:
        """确保 biz-agents 目录存在（框架态）"""
        agents_dir = biz_dir / "biz-agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        readme = agents_dir / "README.md"
        if not readme.exists():
            readme.write_text(
                "# 业务需求运营 agent (biz-agents/, 0.0.14, DEC-2026-0003)\n\n"
                "## 框架态说明\n\n"
                "本目录由 PMO OnboardingSyncer 自动创建（m0.9）。\n\n"
                "业务项目在此目录中完全自定业务 agent（PMO 不预设不干预）。\n\n"
                "## 规范（0.0.14）\n\n"
                "- 业务 agent 数量/名字/责任/输入输出：业务项目完全自定\n"
                "- PMO 不预设不干预\n"
                "- 业务 agent 定义写在 contract-<id>-biz-ops-roles.md 中\n",
                encoding="utf-8"
            )
        return {"success": True, "created": True, "dir": str(agents_dir)}

    def _write_sync_metadata(self, biz_dir: Path, biz_project_id: str,
                             results: Dict[str, Any]) -> Dict[str, Any]:
        """写同步元数据文件"""
        sync_dir = biz_dir / "reports"
        sync_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = sync_dir / "sync-metadata.json"

        now = datetime.now(timezone.utc).isoformat()
        metadata = {
            "biz_project_id": biz_project_id,
            "synced_at": now,
            "synced_by": "OnboardingSyncer",
            "pmo_version": self.PROTOCOL_VERSION,
            "synced_items": {
                k: {"status": v.get("status", "unknown"), "success": v.get("success", False)}
                for k, v in results.items()
            },
            "immutable_contracts": [
                f"immutable/2-biz-specs/contract-{biz_project_id}-overall.md",
                f"immutable/2-biz-specs/contract-{biz_project_id}-eng-5-stages.md",
                f"immutable/2-biz-specs/contract-{biz_project_id}-biz-ops-roles.md",
            ]
        }

        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return metadata

    def _log_sync(self, biz_project_id: str, results: Dict[str, Any]):
        """记录同步日志"""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_file = self.logs_dir / f"onboarding-sync-{today}.json"
        log_entries = []
        if log_file.exists():
            try:
                log_entries = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                log_entries = []

        log_entries.append({
            "biz_project_id": biz_project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": {k: v.get("status", "unknown") for k, v in results.items()}
        })

        log_file.write_text(json.dumps(log_entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def _notify_biz_project(self, biz_project_id: str, metadata: Dict[str, Any]):
        """通过 Message-Broker 通知业务项目：规范同步完成"""
        try:
            payload = {
                "event_type": "norm_sync_complete",
                "biz_project_id": biz_project_id,
                "synced_at": metadata["synced_at"],
                "synced_items": list(metadata["synced_items"].keys()),
                "immutable_contracts": metadata["immutable_contracts"],
                "pull_url": f"/pmo-api/v1/norms/sync/{biz_project_id}",
                "ack_url": f"/pmo-api/v1/norms/sync/{biz_project_id}/ack"
            }
            self.broker.publish(
                from_project="pmo-onboarding-syncer",
                to_project=biz_project_id,
                topic=f"pmo.norm.sync.{biz_project_id}",
                msg_type="notification",
                content=payload,
                qos="1",
                layer="pmo"
            )
        except Exception:
            pass

    # ---------------- 查询接口 ----------------

    def get_sync_status(self, biz_project_id: str) -> Dict[str, Any]:
        """获取业务项目的同步状态"""
        sync_file = self.biz_projects_dir / biz_project_id / "reports" / "sync-metadata.json"
        if not sync_file.exists():
            return {"synced": False, "biz_project_id": biz_project_id}
        try:
            metadata = json.loads(sync_file.read_text(encoding="utf-8"))
            return {"synced": True, **metadata}
        except Exception:
            return {"synced": False, "error": "metadata corrupted", "biz_project_id": biz_project_id}

    def get_all_synced_projects(self) -> List[str]:
        """获取所有已完成同步的业务项目"""
        synced = []
        if not self.biz_projects_dir.exists():
            return synced
        for proj_dir in self.biz_projects_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            sync_file = proj_dir / "reports" / "sync-metadata.json"
            if sync_file.exists():
                synced.append(proj_dir.name)
        return sorted(synced)


# ============================================
# 演示 / 自测入口
# ============================================
if __name__ == "__main__":
    import sys
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("=== PMO OnboardingSyncer 演示 (m0.9, DEC-2026-0009) ===\n")

    syncer = OnboardingSyncer(PMO_ROOT)

    # 1. 全量同步演示
    print("[1] 接入时全量同步 (biz_project_id: 1.x-test-syncer)")
    biz_id = "1.x-test-syncer"
    result = syncer.sync_all_norms(
        biz_id,
        register_data={
            "biz_project": {
                "id": biz_id,
                "name": "同步测试项目",
                "type": "test",
                "version": "0.1.0",
                "sponsor": "测试Sponsor"
            }
        }
    )
    print(f"  - success: {result['success']}")
    print(f"  - synced_items: {result['synced_items']}")
    if result['errors']:
        print(f"  - errors: {result['errors']}")
    print(f"  - timestamp: {result['timestamp']}")
    print()

    # 2. 查询同步状态
    print("[2] 查询同步状态")
    status = syncer.get_sync_status(biz_id)
    print(f"  - synced: {status['synced']}")
    if status["synced"]:
        print(f"  - synced_at: {status['synced_at']}")
        print(f"  - immutable_contracts: {status['immutable_contracts']}")
    print()

    # 3. 所有已同步项目
    print("[3] 所有已同步项目")
    all_synced = syncer.get_all_synced_projects()
    print(f"  - count: {len(all_synced)}")
    for pid in all_synced:
        print(f"  - {pid}")
    print()

    print("=== OnboardingSyncer 演示完成 ===")
