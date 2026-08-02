"""delivery-flow 本地只读自动化命令行入口。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import check_project, current_stage_summary, dry_run, status_summary, summarize_findings, trace_project

EXIT_OK = 0
EXIT_BLOCKED = 1
EXIT_INPUT = 2
EXIT_POLICY = 3
EXIT_INTERNAL = 4


def emit(payload: object, as_json: bool) -> None:
    """统一输出人读摘要或稳定 JSON。"""
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    elif isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {value}")
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="delivery-flow 本地只读一致性检查工具")
    parser.add_argument("command", choices=("check", "trace", "status", "dry-run", "progress"))
    parser.add_argument("--root", default=".", help="消费方项目根目录")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    parser.add_argument("--status-file", help="status 命令指定本地镜像路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "check":
            findings = check_project(root)
            payload = {"findings": findings, "summary": summarize_findings(findings)}
            emit(payload, args.json)
            return EXIT_BLOCKED if payload["summary"]["blocked"] else EXIT_OK
        if args.command == "trace":
            payload = trace_project(root)
            emit(payload, args.json)
            return EXIT_BLOCKED if payload["status"] != "pass" else EXIT_OK
        if args.command == "status":
            status_path = Path(args.status_file).resolve() if args.status_file else None
            payload = status_summary(root, status_path)
            emit(payload, args.json)
            return EXIT_OK
        if args.command == "dry-run":
            payload = dry_run(root)
            emit(payload, args.json)
            return EXIT_BLOCKED if payload["blocked_by"] else EXIT_OK
        if args.command == "progress":
            payload = current_stage_summary(root)
            emit(payload, args.json)
            return EXIT_OK
        return EXIT_INPUT
    except (OSError, UnicodeError, ValueError) as exc:
        emit({"error": str(exc)}, args.json)
        return EXIT_INPUT
    except Exception as exc:  # pragma: no cover - 防止 CLI 泄漏堆栈
        emit({"error": str(exc)}, args.json)
        return EXIT_INTERNAL


if __name__ == "__main__":
    sys.exit(main())
