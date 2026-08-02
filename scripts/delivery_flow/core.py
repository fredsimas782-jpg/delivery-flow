"""交付产物读取、校验和追溯的纯本地实现。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

SPEC_FIELDS = ("Why", "Capabilities", "Constraints", "Non-goals", "Success signal")
STATUS_MAP = {
    "待开发": "planned",
    "开发中": "in_progress",
    "测试中": "in_review",
    "已上线": "done",
    "缺陷": "blocked",
    "优化": "in_progress",
}


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """读取 JSON；错误作为数据返回，避免 CLI 直接崩溃。"""
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "文件不存在"
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)


def markdown_has_heading(path: Path, heading: str) -> bool:
    """检查 Markdown 是否存在指定标题或字段。"""
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(re.search(rf"^\s*#+\s*{re.escape(heading)}\s*:?[ \t]*$", text, re.MULTILINE | re.IGNORECASE))


def find_first(root: Path, patterns: tuple[str, ...]) -> Path | None:
    """按稳定顺序寻找第一个真实项目产物。"""
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        for path in matches:
            if path.is_file() and "template" not in path.name.lower() and "模板" not in path.name and "示范" not in path.name:
                return path
    return None


def load_mapping(root: Path) -> tuple[dict[str, Any] | None, str | None, Path]:
    """读取约定位置的映射表，不自动创建或修复。"""
    path = find_first(root, ("_映射表.json", "**/_映射表.json")) or root / "_映射表.json"
    data, error = read_json(path)
    return data, error, path


def mapping_ids(data: dict[str, Any] | None) -> tuple[set[str], list[str]]:
    """提取三级映射中的本地子任务 ID 和结构错误。"""
    ids: set[str] = set()
    errors: list[str] = []
    if not isinstance(data, dict):
        return ids, ["映射表不是 JSON 对象"]
    tasklists = data.get("tasklists")
    if not isinstance(tasklists, dict):
        return ids, ["缺少 tasklists 对象"]
    for list_name, tasklist in tasklists.items():
        if not isinstance(tasklist, dict):
            errors.append(f"清单 {list_name} 不是对象")
            continue
        parents = tasklist.get("parent_tasks", {})
        if not isinstance(parents, dict):
            errors.append(f"清单 {list_name} 的 parent_tasks 不是对象")
            continue
        for parent_name, parent in parents.items():
            if not isinstance(parent, dict):
                errors.append(f"父任务 {parent_name} 不是对象")
                continue
            subtasks = parent.get("subtasks", {})
            if not isinstance(subtasks, dict):
                errors.append(f"父任务 {parent_name} 的 subtasks 不是对象")
                continue
            for local_id, task_id in subtasks.items():
                if local_id in ids:
                    errors.append(f"本地子任务 ID 重复：{local_id}")
                ids.add(local_id)
                if not isinstance(task_id, str) or not task_id.strip():
                    errors.append(f"子任务 {local_id} 缺少飞书 task_id")
    return ids, errors


def check_project(root: Path) -> list[dict[str, Any]]:
    """执行只读项目检查，结果稳定且不修改任何文件。"""
    findings: list[dict[str, Any]] = []

    def add(item_id: str, status: str, message: str, evidence: list[str] | None = None, severity: str = "error") -> None:
        findings.append({
            "id": item_id,
            "severity": severity,
            "status": status,
            "evidence": evidence or [],
            "message": message,
        })

    spec = root / "SPEC.md"
    missing_fields = [field for field in SPEC_FIELDS if not markdown_has_heading(spec, field)]
    if not spec.is_file():
        add("spec.exists", "fail", "缺少 SPEC.md")
    elif missing_fields:
        add("spec.fields", "fail", f"SPEC 缺少字段：{', '.join(missing_fields)}", [str(spec.relative_to(root))])
    else:
        add("spec.fields", "pass", "SPEC 五字段齐全", [str(spec.relative_to(root))], severity="info")

    confirmation = find_first(root, ("*客户确认*.md", "**/*客户确认*.md"))
    readiness = find_first(root, ("*readiness*.md", "**/*readiness*.md", "**/*技术就绪*.md"))
    acceptance = find_first(root, ("*验收报告*.md", "**/*验收报告*.md"))
    stories = find_first(root, ("stories/**/*.md", "**/*story*.md", "**/*stories*.md"))
    for item_id, label, path in (
        ("gate.client", "客户确认记录", confirmation),
        ("gate.readiness", "技术就绪报告", readiness),
        ("gate.acceptance", "验收报告", acceptance),
        ("stories.exists", "Story 文档", stories),
    ):
        if path:
            add(item_id, "pass", f"已找到{label}", [str(path.relative_to(root))], severity="info")
        else:
            add(item_id, "unknown", f"未找到{label}，需要人工确认", severity="warning")

    mapping, mapping_error, mapping_path = load_mapping(root)
    if mapping_error:
        add("mapping.valid", "unknown" if mapping_error == "文件不存在" else "fail", f"映射表：{mapping_error}", [str(mapping_path.relative_to(root))], severity="warning" if mapping_error == "文件不存在" else "error")
    else:
        _, errors = mapping_ids(mapping)
        if errors:
            add("mapping.valid", "fail", "映射表结构存在问题", errors)
        else:
            add("mapping.valid", "pass", "映射表三级结构可读取", [str(mapping_path.relative_to(root))], severity="info")

    # 后段产物存在而前置关卡缺失时，明确报告流程乱序。
    if stories and not confirmation:
        add("order.client-before-story", "fail", "已存在 Story，但没有客户确认记录")
    if mapping and not readiness:
        add("order.readiness-before-feishu", "fail", "已存在飞书映射，但没有技术就绪报告")
    return findings


def summarize_findings(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """汇总检查结果，并保留未知状态不等同于通过。"""
    counts = Counter(item["status"] for item in findings)
    return {
        "pass": counts.get("pass", 0),
        "warn": counts.get("warn", 0) + counts.get("unknown", 0),
        "fail": counts.get("fail", 0),
        "blocked": counts.get("fail", 0) > 0 or counts.get("unknown", 0) > 0,
    }


def trace_project(root: Path) -> dict[str, Any]:
    """基于文件和映射表生成只读追溯摘要，不伪造缺失链路。"""
    mapping, error, mapping_path = load_mapping(root)
    ids, mapping_errors = mapping_ids(mapping)
    links = {
        "spec": (root / "SPEC.md").is_file(),
        "stories": find_first(root, ("stories/**/*.md", "**/*story*.md", "**/*stories*.md")) is not None,
        "mapping": error is None and not mapping_errors,
        "evaluation": find_first(root, ("*评测报告*.md", "**/*评测报告*.md")) is not None,
        "acceptance": find_first(root, ("*验收报告*.md", "**/*验收报告*.md")) is not None,
    }
    missing = [name for name, present in links.items() if not present]
    return {
        "links": links,
        "mapping_path": str(mapping_path.relative_to(root)),
        "mapped_subtask_count": len(ids),
        "missing": missing,
        "mapping_errors": mapping_errors,
        "status": "pass" if not missing and not mapping_errors else "incomplete",
    }


def read_simple_status(path: Path) -> list[dict[str, str]]:
    """读取常见的 story/status 两列 YAML；复杂 YAML 留给未来适配器。"""
    if not path.is_file():
        return []
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*(-\s*)?([^:#]+):\s*([^#]+?)\s*$", raw)
        if not match:
            continue
        key = match.group(2).strip().lower()
        value = match.group(3).strip().strip('"\'')
        if key in {"story", "id", "key"} and current:
            rows.append(current)
            current = {}
        if key in {"story", "id", "key", "status", "blocked_by"}:
            current[key] = value
    if current:
        rows.append(current)
    return rows


def status_summary(root: Path, status_path: Path | None = None) -> dict[str, Any]:
    """聚合本地状态镜像，明确标记其只读属性。"""
    path = status_path or root / "sprint-status.yaml"
    rows = read_simple_status(path)
    values = [row["status"] for row in rows if row.get("status")]
    return {
        "source": "local-read-only-mirror",
        "authority": "feishu",
        "path": str(path.relative_to(root)) if path.is_absolute() and path.is_relative_to(root) else str(path),
        "exists": path.is_file(),
        "row_count": len(rows),
        "status_counts": dict(Counter(values)),
        "note": "本地状态只读，不能反向写飞书",
    }


STAGES_ORDER = (
    "requirements", "analysis", "prd", "ux", "prototype",
    "client_gate", "architecture", "tech_readiness",
    "story_breakdown", "feishu_sync", "development",
    "eval", "qa", "acceptance_gate",
)


def read_progress(path: Path) -> dict[str, Any] | None:
    """读取 project-progress.yaml（最小化解析，不依赖第三方 YAML 库）。"""
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    result: dict[str, Any] = {"project": "", "current_stage": "", "stages": {}}
    current_stage: str | None = None
    current_stage_data: dict[str, str] = {}
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        # 顶层 key: value
        if indent == 0 and ":" in stripped:
            key, _, val = stripped.partition(":")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key in ("project", "current_stage"):
                result[key] = val
            elif key == "stages":
                continue
        # stages 下的子 key（缩进 2）
        elif indent == 2 and ":" in stripped:
            if current_stage and current_stage_data:
                result["stages"][current_stage] = current_stage_data
            stage_name = stripped.rstrip(":").strip()
            current_stage = stage_name
            current_stage_data = {}
        # stage 内的字段（缩进 4）
        elif indent >= 4 and ":" in stripped:
            key, _, val = stripped.partition(":")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if current_stage and key:
                current_stage_data[key] = val
    if current_stage and current_stage_data:
        result["stages"][current_stage] = current_stage_data
    return result


def current_stage_summary(root: Path) -> dict[str, Any]:
    """汇总当前流水线阶段，优先读 project-progress.yaml，回退到产物扫描。"""
    progress_path = root / "project-progress.yaml"
    progress = read_progress(progress_path)
    if progress:
        # 从 progress.yaml 读取
        current = progress.get("current_stage", "")
        stages = progress.get("stages", {})
        current_info = stages.get(current, {})
        # 找到下一个 pending 阶段
        next_stage = ""
        found_current = False
        for stage_id in STAGES_ORDER:
            if stage_id == current:
                found_current = True
                continue
            if found_current and stages.get(stage_id, {}).get("status") == "pending":
                next_stage = stage_id
                break
        return {
            "source": "project-progress.yaml",
            "project": progress.get("project", ""),
            "current_stage": current,
            "current_status": current_info.get("status", ""),
            "next_stage": next_stage,
            "completed_count": sum(1 for s in stages.values() if s.get("status") == "done"),
            "total_stages": len(STAGES_ORDER),
            "stages": {k: v.get("status", "pending") for k, v in stages.items()},
        }
    # 回退：通过产物扫描推断（与 onboarding step 3 逻辑一致）
    checks = [
        ("prd", root / "PRD.md"),
        ("ux", root / "UX.md"),
        ("prototype", root / "prototype" / "index.html"),
        ("client_gate", find_first(root, ("*客户确认*.md", "**/*客户确认*.md"))),
        ("architecture", find_first(root, ("AD-*.md", "**/AD-*.md"))),
        ("tech_readiness", find_first(root, ("*readiness*.md", "**/*readiness*.md"))),
        ("story_breakdown", find_first(root, ("stories/**/*.md",))),
        ("feishu_sync", find_first(root, ("_映射表.json", "**/_映射表.json"))),
        ("eval", find_first(root, ("*评测报告*.md", "**/*评测报告*.md"))),
        ("acceptance_gate", find_first(root, ("*验收报告*.md", "**/*验收报告*.md"))),
    ]
    inferred = "requirements"
    for stage_id, path_or_none in checks:
        if path_or_none and (isinstance(path_or_none, Path) and path_or_none.exists() if isinstance(path_or_none, Path) else True):
            inferred = stage_id
    return {
        "source": "inferred-from-files",
        "current_stage": inferred,
        "note": "未找到 project-progress.yaml，根据产物存在性推断。建议创建 project-progress.yaml 以获得准确追踪。",
    }


def dry_run(root: Path) -> dict[str, Any]:
    """生成无副作用的飞书任务预览。"""
    mapping, error, path = load_mapping(root)
    ids, errors = mapping_ids(mapping)
    blocked = []
    if error and error != "文件不存在":
        blocked.append(f"映射表不可读取：{error}")
    blocked.extend(errors)
    return {
        "operations": [],
        "blocked_by": blocked,
        "would_write": [str(path.relative_to(root))],
        "network": False,
        "side_effects": False,
        "mapped_subtask_count": len(ids),
        "note": "当前仅输出计划，不创建或更新飞书任务，不写入映射表",
    }
