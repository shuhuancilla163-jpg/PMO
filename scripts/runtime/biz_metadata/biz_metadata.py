"""
PMO 业务元数据 3 项 (biz_metadata.py, m2.1, DEC-2026-0005)
- E1 业务项目元数据 (register.yaml): 业务项目身份信息, PMO 存
- E2 业务数据 schema (data-schema.yaml): 业务项目数据模型, 业务项目定义, PMO 存
- E3 业务术语表 (glossary.yaml): 业务项目专业术语, 业务 agent 定义, PMO 验证
- 业务项目接入 5 步流程前 3 步基于 m2.1
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


def _load_yaml_simple(content: str) -> Any:
    """简化版 YAML 解析 (支持嵌套 dict + list of dict)

    支持:
    - key: value
    - 嵌套 dict (通过缩进, 2 空格)
    - list of dict:
        - key1: val1
        - key2: val2
    - 简单 list (- item)
    - # 注释
    - 字符串 / 数字 / bool
    """
    # 1. 移除注释行
    raw_lines = content.split("\n")
    lines = []
    for line in raw_lines:
        # 移除行内 # 注释 (不在引号内)
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        # 简单处理: 只移除行尾的 # (假设业务元数据没有 # 字符串)
        # 移除 "key: val # 注释" 格式
        if " #" in line:
            line = line[:line.index(" #")]
        lines.append(line)
    if not lines:
        return {}
    return _parse_block(lines, 0, 0)[0]


def _parse_block(lines: List[str], start: int, base_indent: int) -> tuple:
    """解析一个 block (dict or list of dict)

    Returns: (parsed_object, next_index)
    """
    if start >= len(lines):
        return {}, start
    first_line = lines[start]
    first_indent = len(first_line) - len(first_line.lstrip())
    first_stripped = first_line.strip()
    # 判断是 list 还是 dict
    if first_stripped.startswith("- "):
        return _parse_list(lines, start, base_indent)
    else:
        return _parse_dict(lines, start, base_indent)


def _parse_dict(lines: List[str], start: int, base_indent: int) -> tuple:
    """解析 dict block"""
    result = {}
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break
        if indent > base_indent:
            # 不应该, 跳过
            i += 1
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            # list 出现在 dict 内 (list of dict), 处理不了, 跳过
            break
        if ":" not in stripped:
            i += 1
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            # 嵌套, 看下一行
            if i + 1 < len(lines) and lines[i + 1].strip():
                next_indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                if next_indent > base_indent:
                    sub, next_i = _parse_block(lines, i + 1, next_indent)
                    result[key] = sub
                    i = next_i
                    continue
            result[key] = ""
            i += 1
        else:
            result[key] = _parse_value(value)
            i += 1
    return result, i


def _parse_list(lines: List[str], start: int, base_indent: int) -> tuple:
    """解析 list block (支持 list of dict)"""
    result = []
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break
        if indent > base_indent:
            i += 1
            continue
        stripped = line.strip()
        if not stripped.startswith("- "):
            break
        content = stripped[2:].strip()
        if not content:
            # list item 是 dict, 后续行是 dict 内容
            sub_indent = base_indent + 2
            if i + 1 < len(lines) and lines[i + 1].strip():
                next_line = lines[i + 1]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > base_indent:
                    sub, next_i = _parse_block(lines, i + 1, next_indent)
                    result.append(sub)
                    i = next_i
                    continue
            result.append({})
            i += 1
        elif ":" in content:
            # list item 是 dict (单行形式: - key: val)
            item = {}
            key, _, value = content.partition(":")
            item[key.strip()] = _parse_value(value.strip())
            # 后续行可能是同一 dict 的更多字段
            i += 1
            while i < len(lines):
                line = lines[i]
                if not line.strip():
                    i += 1
                    continue
                next_indent = len(line) - len(line.lstrip())
                if next_indent <= base_indent:
                    break
                if next_indent > base_indent + 2:
                    i += 1
                    continue
                cont_stripped = line.strip()
                if cont_stripped.startswith("- "):
                    break
                if ":" in cont_stripped:
                    k, _, v = cont_stripped.partition(":")
                    v = v.strip()
                    if v == "":
                        # 嵌套
                        if i + 1 < len(lines) and lines[i + 1].strip():
                            next_next = lines[i + 1]
                            nn_indent = len(next_next) - len(next_next.lstrip())
                            if nn_indent > next_indent:
                                sub, next_i = _parse_block(lines, i + 1, nn_indent)
                                item[k.strip()] = sub
                                i = next_i
                                continue
                        item[k.strip()] = ""
                    else:
                        item[k.strip()] = _parse_value(v)
                i += 1
            result.append(item)
        else:
            # 简单值
            result.append(_parse_value(content))
            i += 1
    return result, i


def _parse_value(s: str) -> Any:
    """解析 YAML 简单值 (支持 inline list [a, b, c])"""
    s = s.strip()
    if not s:
        return ""
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    if s.lower() in ("null", "~", ""):
        return None
    # inline list: [a, b, c]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        items = [item.strip() for item in inner.split(",")]
        return [_parse_value(item) for item in items]
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        pass
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def _yaml_dump_simple(data: Any, indent: int = 0) -> str:
    """简化版 YAML 序列化 (用于存到 PMO config 的 JSON)"""
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(" " * indent + f"{k}:")
                lines.append(_yaml_dump_simple(v, indent + 2))
            else:
                lines.append(" " * indent + f"{k}: {_format_value(v)}")
        return "\n".join(lines)
    elif isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(" " * indent + "-")
                lines.append(_yaml_dump_simple(item, indent + 2))
            else:
                lines.append(" " * indent + f"- {_format_value(item)}")
        return "\n".join(lines)
    return ""


def _format_value(v: Any) -> str:
    """格式化 YAML 值"""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if v is None:
        return "null"
    s = str(v)
    if any(c in s for c in [":", "#", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`", "{", "}", "[", "]"]):
        return f'"{s}"'
    return s


# ============================================
# 5 阶段研发 agent role (0.0.13)
# ============================================
ENG_5_STAGES_ROLES = {
    "Requirement-Engineer",
    "Development-Engineer",
    "Test-Engineer",
    "Operations-Engineer",
    "Evaluation-Engineer"
}


# ============================================
# 业务项目元数据存储管理器 (PMO 实例用)
# ============================================
class BizMetadataStore:
    """PMO 业务元数据存储 (m2.1, DEC-2026-0005)

    职责:
    - 业务项目 E1/E2/E3 加载 (从 biz-projects/<id>/)
    - PMO 存 (到 config/biz-meta/<id>*.json)
    - 业务元数据验证 (E1 必填字段 / E2 schema / E3 术语)
    - 业务 agent 与 5 阶段研发 role 边界 (DEC-2026-0003)
    """

    def __init__(self, pmo_root: str):
        self.pmo_root = Path(pmo_root)
        self.biz_projects_dir = self.pmo_root / "biz-projects"
        self.biz_meta_dir = self.pmo_root / "config" / "biz-meta"
        self.biz_meta_dir.mkdir(parents=True, exist_ok=True)
        # 业务项目元数据索引
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载 YAML 文件 (内置简化解析, 不依赖 pyyaml)"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return _load_yaml_simple(content)

    # ---------------- E1 业务项目元数据 ----------------
    def load_e1(self, biz_project_id: str) -> Dict[str, Any]:
        """加载 E1 业务项目元数据 (register.yaml)"""
        register_file = self.biz_projects_dir / biz_project_id / "register.yaml"
        if not register_file.exists():
            return {"success": False, "error": f"register.yaml 不存在: {register_file}"}
        try:
            e1 = self._load_yaml_file(register_file)
        except Exception as e:
            return {"success": False, "error": f"YAML 解析失败: {e}"}
        if e1 is None or not isinstance(e1, dict):
            return {"success": False, "error": "YAML 解析结果为空或非 dict"}
        # 验证 E1
        validation = self._validate_e1(e1)
        if not validation["valid"]:
            return {"success": False, "error": f"E1 验证失败: {validation['errors']}"}
        # 存到 PMO config
        self._save_to_pmo(biz_project_id, "e1", e1)
        if biz_project_id not in self.metadata:
            self.metadata[biz_project_id] = {}
        self.metadata[biz_project_id]["e1"] = e1
        return {"success": True, "biz_project_id": biz_project_id, "e1": e1}

    def _validate_e1(self, e1: Dict[str, Any]) -> Dict[str, Any]:
        """验证 E1 业务项目元数据 (强制字段, 0.0.16 第 2 节)"""
        errors = []
        # 1. biz_project 必填
        bp = e1.get("biz_project", {})
        for field in ["id", "name", "type", "version", "sponsor", "registered_at"]:
            if not bp.get(field):
                errors.append(f"biz_project.{field} 必填")
        # 2. pmo_supervision 必填
        ps = e1.get("pmo_supervision", {})
        if "enabled" not in ps:
            errors.append("pmo_supervision.enabled 必填")
        if not ps.get("state"):
            errors.append("pmo_supervision.state 必填")
        # 3. quota_4d 必填
        quota = ps.get("quota_4d", {})
        for dim in ["token", "time", "storage", "concurrency"]:
            if dim not in quota:
                errors.append(f"pmo_supervision.quota_4d.{dim} 必填")
        # 4. isolation_3d 必填
        iso = ps.get("isolation_3d", {})
        for dim in ["data", "config", "state"]:
            if dim not in iso:
                errors.append(f"pmo_supervision.isolation_3d.{dim} 必填")
        # 5. agent_categories 必填
        ac = e1.get("agent_categories", {})
        if "eng_roles" not in ac:
            errors.append("agent_categories.eng_roles 必填")
        if "biz_agents" not in ac:
            errors.append("agent_categories.biz_agents 必填")
        # 6. compliance_2_layers 必填
        c2l = e1.get("compliance_2_layers", {})
        if "layer_1_overall" not in c2l:
            errors.append("compliance_2_layers.layer_1_overall 必填")
        if "layer_2_eng_5_stages" not in c2l:
            errors.append("compliance_2_layers.layer_2_eng_5_stages 必填")
        # 7. m2_6_7_items 必填
        m27 = e1.get("m2_6_7_items", {})
        for item in ["registration", "state_machine", "quota_4d", "archive_4_levels",
                     "isolation_3d", "alerting_3_levels", "checklist_6_plus_3"]:
            if item not in m27:
                errors.append(f"m2_6_7_items.{item} 必填")
        return {"valid": len(errors) == 0, "errors": errors}

    # ---------------- E2 业务数据 schema ----------------
    def load_e2(self, biz_project_id: str) -> Dict[str, Any]:
        """加载 E2 业务数据 schema (data-schema.yaml)"""
        schema_file = self.biz_projects_dir / biz_project_id / "data-schema.yaml"
        if not schema_file.exists():
            return {"success": False, "error": f"data-schema.yaml 不存在: {schema_file}"}
        try:
            e2 = self._load_yaml_file(schema_file)
        except Exception as e:
            return {"success": False, "error": f"YAML 解析失败: {e}"}
        if e2 is None or not isinstance(e2, dict):
            return {"success": False, "error": "YAML 解析结果为空或非 dict"}
        # 验证 E2
        validation = self._validate_e2(e2)
        if not validation["valid"]:
            return {"success": False, "error": f"E2 验证失败: {validation['errors']}"}
        # 存到 PMO config
        self._save_to_pmo(biz_project_id, "e2", e2)
        if biz_project_id not in self.metadata:
            self.metadata[biz_project_id] = {}
        self.metadata[biz_project_id]["e2"] = e2
        return {"success": True, "biz_project_id": biz_project_id, "e2": e2}

    def _validate_e2(self, e2: Dict[str, Any]) -> Dict[str, Any]:
        """验证 E2 业务数据 schema (0.0.16 第 3 节)"""
        errors = []
        schema = e2.get("biz_data_schema", {})
        if not schema.get("version"):
            errors.append("biz_data_schema.version 必填")
        if schema.get("defined_by") != "biz_project":
            errors.append("biz_data_schema.defined_by 必须为 'biz_project'")
        if schema.get("stored_by") != "pmo_instance":
            errors.append("biz_data_schema.stored_by 必须为 'pmo_instance'")
        # 验证实体
        entities = schema.get("entities", [])
        entity_names = set()
        for entity in entities:
            ename = entity.get("name")
            if not ename:
                errors.append("entity.name 必填")
                continue
            if ename in entity_names:
                errors.append(f"entity.name 重复: {ename}")
            entity_names.add(ename)
            # 验证字段
            fields = entity.get("fields", [])
            field_names = set()
            for field in fields:
                fname = field.get("name")
                if not fname:
                    errors.append(f"entity {ename} field.name 必填")
                    continue
                if fname in field_names:
                    errors.append(f"entity {ename} field.name 重复: {fname}")
                field_names.add(fname)
                if not field.get("type"):
                    errors.append(f"entity {ename} field {fname} type 必填")
                # enum 类型必须有 values
                if field.get("type") == "enum" and not field.get("values"):
                    errors.append(f"entity {ename} field {fname} type=enum 必须有 values")
            # 验证 primary_key
            pk = entity.get("primary_key", [])
            for pk_field in pk:
                if pk_field not in field_names:
                    errors.append(f"entity {ename} primary_key {pk_field} 不在 fields 内")
        # 验证 foreign_key
        for entity in entities:
            for field in entity.get("fields", []):
                fk = field.get("foreign_key", "")
                if fk:
                    if "." not in fk:
                        errors.append(f"entity {entity['name']} field {field.get('name')} foreign_key 格式错误: {fk}")
                    else:
                        target_entity, _ = fk.split(".", 1)
                        if target_entity not in entity_names:
                            errors.append(f"entity {entity['name']} field {field.get('name')} foreign_key 目标实体不存在: {target_entity}")
        return {"valid": len(errors) == 0, "errors": errors}

    # ---------------- E3 业务术语表 ----------------
    def load_e3(self, biz_project_id: str) -> Dict[str, Any]:
        """加载 E3 业务术语表 (glossary.yaml)"""
        glossary_file = self.biz_projects_dir / biz_project_id / "glossary.yaml"
        if not glossary_file.exists():
            return {"success": False, "error": f"glossary.yaml 不存在: {glossary_file}"}
        try:
            e3 = self._load_yaml_file(glossary_file)
        except Exception as e:
            return {"success": False, "error": f"YAML 解析失败: {e}"}
        if e3 is None or not isinstance(e3, dict):
            return {"success": False, "error": "YAML 解析结果为空或非 dict"}
        # 验证 E3
        validation = self._validate_e3(e3)
        if not validation["valid"]:
            return {"success": False, "error": f"E3 验证失败: {validation['errors']}"}
        # 存到 PMO config
        self._save_to_pmo(biz_project_id, "e3", e3)
        if biz_project_id not in self.metadata:
            self.metadata[biz_project_id] = {}
        self.metadata[biz_project_id]["e3"] = e3
        return {"success": True, "biz_project_id": biz_project_id, "e3": e3}

    def _validate_e3(self, e3: Dict[str, Any]) -> Dict[str, Any]:
        """验证 E3 业务术语表 (0.0.16 第 4 节)"""
        errors = []
        glossary = e3.get("biz_glossary", {})
        if not glossary.get("version"):
            errors.append("biz_glossary.version 必填")
        if glossary.get("defined_by") != "biz_project":
            errors.append("biz_glossary.defined_by 必须为 'biz_project'")
        if glossary.get("validated_by") != "pmo_instance":
            errors.append("biz_glossary.validated_by 必须为 'pmo_instance'")
        # 验证 terms
        terms = glossary.get("terms", [])
        term_names = set()
        valid_categories = {"entity", "state", "metric", "action", "role"}
        for term in terms:
            tname = term.get("term")
            if not tname:
                errors.append("term.term 必填")
                continue
            if tname in term_names:
                errors.append(f"term.term 重复: {tname}")
            term_names.add(tname)
            if not term.get("definition"):
                errors.append(f"term {tname} definition 必填")
            cat = term.get("category")
            if cat not in valid_categories:
                errors.append(f"term {tname} category 非法: {cat} (合法: {valid_categories})")
        # 验证 roles (业务 agent)
        roles = glossary.get("roles", [])
        role_names = set()
        for role in roles:
            rname = role.get("role")
            if not rname:
                errors.append("role.role 必填")
                continue
            if rname in role_names:
                errors.append(f"role.role 重复: {rname}")
            role_names.add(rname)
            # DEC-2026-0003: 业务 agent role 不与 5 阶段研发 role 重名
            if rname in ENG_5_STAGES_ROLES:
                errors.append(f"role {rname} 与 5 阶段研发 agent role 重名, 业务自管 (DEC-2026-0003)")
            if not role.get("identity"):
                errors.append(f"role {rname} identity 必填")
            if not role.get("scope"):
                errors.append(f"role {rname} scope 必填")
            # 验证 uses_terms 在术语表内
            for ut in role.get("uses_terms", []):
                if ut not in term_names:
                    errors.append(f"role {rname} uses_term {ut} 不在 terms 内")
        return {"valid": len(errors) == 0, "errors": errors}

    # ---------------- 业务项目接入 (E1+E2+E3 一起) ----------------
    def onboard_biz_project(self, biz_project_id: str) -> Dict[str, Any]:
        """业务项目接入 PMO (E1+E2+E3, m2.1)"""
        results = {"biz_project_id": biz_project_id, "steps": {}}
        # E1
        e1_result = self.load_e1(biz_project_id)
        results["steps"]["E1"] = e1_result
        if not e1_result["success"]:
            results["success"] = False
            results["error"] = "E1 失败, 业务项目未接入"
            return results
        # E2
        e2_result = self.load_e2(biz_project_id)
        results["steps"]["E2"] = e2_result
        if not e2_result["success"]:
            results["success"] = False
            results["error"] = "E2 失败, 业务项目未接入"
            return results
        # E3
        e3_result = self.load_e3(biz_project_id)
        results["steps"]["E3"] = e3_result
        if not e3_result["success"]:
            results["success"] = False
            results["error"] = "E3 失败, 业务项目未接入"
            return results
        # 全部成功
        results["success"] = True
        results["onboarded_at"] = datetime.now(timezone.utc).isoformat()
        return results

    # ---------------- 存储到 PMO config ----------------
    def _save_to_pmo(self, biz_project_id: str, item: str, data: Dict[str, Any]):
        """存到 PMO config/biz-meta/<id>-<item>.json"""
        suffix = "schema" if item == "e2" else ("glossary" if item == "e3" else "")
        file_name = f"{biz_project_id}{('-' + suffix) if suffix else ''}.json"
        target = self.biz_meta_dir / file_name
        with open(target, "w", encoding="utf-8") as f:
            json.dump({
                "biz_project_id": biz_project_id,
                "item": item.upper(),
                "loaded_at": datetime.now(timezone.utc).isoformat(),
                "data": data
            }, f, ensure_ascii=False, indent=2)

    # ---------------- 查询 ----------------
    def get_metadata(self, biz_project_id: str, item: str = None) -> Dict[str, Any]:
        """获取业务项目元数据"""
        if biz_project_id not in self.metadata:
            return {"error": f"业务项目 {biz_project_id} 未接入"}
        if item:
            return self.metadata[biz_project_id].get(item.upper().lower(), {"error": f"{item} 不存在"})
        return self.metadata[biz_project_id]

    def list_onboarded_projects(self) -> List[str]:
        """列出已接入的业务项目"""
        return list(self.metadata.keys())


# ============================================
# 演示 / 自测
# ============================================
if __name__ == "__main__":
    PMO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    print("=== PMO 业务元数据 3 项 (m2.1, DEC-2026-0005) 演示 ===\n")

    store = BizMetadataStore(PMO_ROOT)

    # 1. 业务项目 1.1-pmo-self 接入
    print("[1] 业务项目 1.1-pmo-self 接入 (E1+E2+E3)")
    result = store.onboard_biz_project("1.1-pmo-self")
    if result["success"]:
        print(f"  - 1.1-pmo-self 接入成功")
        print(f"  - 步骤: {list(result['steps'].keys())}")
    else:
        print(f"  - 1.1-pmo-self 接入失败: {result.get('error')}")
        for k, v in result["steps"].items():
            print(f"    - {k}: {v}")
    print()

    # 2. 业务项目 1.x-biz-template 框架态说明
    print("[2] 业务项目 1.x-biz-template (框架态)")
    print("  - 1.x-biz-template 是通用业务项目骨架模板")
    print("  - 具体业务 domain 由 Sponsor 后续注入")
    print("  - 不参与 E1/E2/E3 验证 (template 状态)")
    print("  - 具体业务示例在 1.x-examples/quant-finance/ (仅供参考)")
    print()

    # 3. 查询元数据
    print("[3] 查询业务项目元数据")
    for pid in store.list_onboarded_projects():
        meta = store.get_metadata(pid)
        e1_name = meta.get("e1", {}).get("biz_project", {}).get("name", "N/A")
        e2_entities = len(meta.get("e2", {}).get("biz_data_schema", {}).get("entities", []))
        e3_terms = len(meta.get("e3", {}).get("biz_glossary", {}).get("terms", []))
        e3_roles = len(meta.get("e3", {}).get("biz_glossary", {}).get("roles", []))
        print(f"  - {pid}: 名称={e1_name}, E2 实体={e2_entities} 个, E3 术语={e3_terms} 个, E3 角色={e3_roles} 个")
    print()

    # 4. 验证业务 agent role 不与 5 阶段研发 role 重名
    print("[4] 验证业务 agent role 不与 5 阶段研发 role 重名 (DEC-2026-0003)")
    for pid in store.list_onboarded_projects():
        meta = store.get_metadata(pid)
        e3_roles = meta.get("e3", {}).get("biz_glossary", {}).get("roles", [])
        for role in e3_roles:
            rname = role.get("role", "")
            conflict = "❌ 冲突" if rname in ENG_5_STAGES_ROLES else "✅ OK"
            print(f"  - {pid}: {rname} → {conflict}")
    print()

    # 5. PMO 存储验证
    print("[5] PMO 存储验证 (config/biz-meta/)")
    for json_file in sorted(store.biz_meta_dir.glob("*.json")):
        print(f"  - {json_file.name}: {json_file.stat().st_size} bytes")
    print()

    print("=== m2.1 业务元数据 3 项演示完成 ===")
