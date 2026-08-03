import json
import tempfile
import unittest
from pathlib import Path

from scripts.delivery_flow.core import (
    check_project,
    current_stage_summary,
    dry_run,
    read_progress,
    read_trace_id,
    status_summary,
    trace_project,
)


class DeliveryCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "SPEC.md").write_text(
            "# SPEC\n\n## Why\n问题\n## Capabilities\n能力\n## Constraints\n约束\n## Non-goals\n不做\n## Success signal\n成功\n",
            encoding="utf-8",
        )
        (self.root / "客户确认记录-2026-07-31.md").write_text("# 客户确认", encoding="utf-8")
        (self.root / "技术就绪-readiness.md").write_text("# readiness", encoding="utf-8")
        (self.root / "验收报告-2026-07-31.md").write_text("# 验收报告", encoding="utf-8")
        (self.root / "评测报告-2026-07-31.md").write_text("# 评测报告", encoding="utf-8")
        (self.root / "stories").mkdir()
        (self.root / "stories" / "story-a.md").write_text("# Story A\nAC", encoding="utf-8")
        (self.root / "_映射表.json").write_text(
            json.dumps({"tasklists": {"模块": {"guid": "list-1", "parent_tasks": {"Story A": {"guid": "parent-1", "subtasks": {"A-1": "task-1"}}}}}}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_check_passes_complete_fixture(self):
        findings = check_project(self.root)
        self.assertFalse(any(item["status"] == "fail" for item in findings))

    def test_trace_reports_complete_chain(self):
        result = trace_project(self.root)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["mapped_subtask_count"], 1)

    def test_dry_run_has_no_side_effect(self):
        before = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        result = dry_run(self.root)
        after = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        self.assertFalse(result["side_effects"])
        self.assertEqual(before, after)
        self.assertFalse(result["network"])

    def test_status_marks_local_mirror(self):
        status = self.root / "sprint-status.yaml"
        status.write_text("- story: A-1\n  status: done\n", encoding="utf-8")
        result = status_summary(self.root)
        self.assertEqual(result["source"], "local-read-only-mirror")
        self.assertEqual(result["authority"], "feishu")
        self.assertEqual(result["status_counts"], {"done": 1})

    def test_read_progress_parses_yaml(self):
        progress_file = self.root / "project-progress.yaml"
        progress_file.write_text(
            'project: "测试项目"\ncurrent_stage: "client_gate"\nstages:\n'
            '  requirements:\n    status: done\n    completed_at: "2026-07-20"\n'
            '  client_gate:\n    status: in_progress\n    started_at: "2026-07-30"\n'
            '  architecture:\n    status: pending\n',
            encoding="utf-8",
        )
        result = read_progress(progress_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["project"], "测试项目")
        self.assertEqual(result["current_stage"], "client_gate")
        self.assertEqual(result["stages"]["requirements"]["status"], "done")
        self.assertEqual(result["stages"]["architecture"]["status"], "pending")

    def test_read_progress_returns_none_when_missing(self):
        result = read_progress(self.root / "nonexistent.yaml")
        self.assertIsNone(result)

    def test_progress_summary_from_file(self):
        progress_file = self.root / "project-progress.yaml"
        progress_file.write_text(
            'project: "示例"\ncurrent_stage: "architecture"\nstages:\n'
            '  requirements:\n    status: done\n  analysis:\n    status: done\n'
            '  prd:\n    status: done\n  prototype:\n    status: done\n'
            '  client_gate:\n    status: done\n  architecture:\n    status: in_progress\n'
            '  tech_readiness:\n    status: pending\n',
            encoding="utf-8",
        )
        result = current_stage_summary(self.root)
        self.assertEqual(result["source"], "project-progress.yaml")
        self.assertEqual(result["current_stage"], "architecture")
        self.assertEqual(result["completed_count"], 5)
        self.assertEqual(result["next_stage"], "tech_readiness")

    def test_progress_summary_fallback_to_files(self):
        # 没有 progress.yaml 时回退到产物扫描
        result = current_stage_summary(self.root)
        self.assertEqual(result["source"], "inferred-from-files")
        self.assertIn("note", result)

    # —— 售前上游：Trace 根与上游链路 ——

    def test_read_trace_id_from_spec_header(self):
        # 商机编号写在 SPEC.md 头部引用行时优先读取
        (self.root / "SPEC.md").write_text(
            "> 商机编号: OPP-2026-007\n\n# SPEC\n\n## Why\n问题\n",
            encoding="utf-8",
        )
        self.assertEqual(read_trace_id(self.root), "OPP-2026-007")

    def test_read_trace_id_fallback_to_progress(self):
        # SPEC 无引用行时回退到 project-progress.yaml 顶层 trace_id
        (self.root / "project-progress.yaml").write_text(
            'project: "示例"\ntrace_id: "OPP-2026-009"\ncurrent_stage: "requirements"\nstages:\n'
            '  requirements:\n    status: in_progress\n',
            encoding="utf-8",
        )
        self.assertEqual(read_trace_id(self.root), "OPP-2026-009")

    def test_read_trace_id_absent(self):
        # 既无 SPEC 引用行也无 progress 时返回空串（不伪造）
        self.assertEqual(read_trace_id(self.root), "")

    def test_trace_includes_upstream_when_trace_id_present(self):
        # 存在商机编号 Trace 根时，链路向上游延伸到商机/签约
        (self.root / "SPEC.md").write_text(
            "> 商机编号: OPP-2026-001\n\n# SPEC\n\n## Why\n问题\n## Capabilities\n能力\n"
            "## Constraints\n约束\n## Non-goals\n不做\n## Success signal\n成功\n",
            encoding="utf-8",
        )
        (self.root / "商机档案-2026-07-10.md").write_text("# 商机档案", encoding="utf-8")
        (self.root / "立项包.md").write_text("# 立项包", encoding="utf-8")
        result = trace_project(self.root)
        self.assertEqual(result["trace_id"], "OPP-2026-001")
        self.assertIn("opportunity", result["links"])
        self.assertIn("deal", result["links"])
        self.assertTrue(result["links"]["opportunity"])
        self.assertTrue(result["links"]["deal"])
        self.assertEqual(result["status"], "pass")

    def test_trace_reports_missing_upstream(self):
        # 有 Trace 根但缺立项包时，如实报告缺链而非隐藏
        (self.root / "SPEC.md").write_text(
            "> 商机编号: OPP-2026-002\n\n# SPEC\n\n## Why\n问题\n## Capabilities\n能力\n"
            "## Constraints\n约束\n## Non-goals\n不做\n## Success signal\n成功\n",
            encoding="utf-8",
        )
        (self.root / "商机档案-2026-07-10.md").write_text("# 商机档案", encoding="utf-8")
        result = trace_project(self.root)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("deal", result["missing"])

    def test_trace_omits_upstream_without_trace_id(self):
        # 无售前的存量项目（无商机编号）不应被判定缺上游链路
        result = trace_project(self.root)
        self.assertEqual(result["trace_id"], "")
        self.assertNotIn("opportunity", result["links"])
        self.assertNotIn("deal", result["links"])

    def test_progress_summary_recognizes_presales_stages(self):
        # project-progress.yaml 覆盖售前上游三阶段
        progress_file = self.root / "project-progress.yaml"
        progress_file.write_text(
            'project: "示例"\ntrace_id: "OPP-2026-001"\ncurrent_stage: "proposal"\nstages:\n'
            '  opportunity:\n    status: done\n  proposal:\n    status: in_progress\n'
            '  deal_gate:\n    status: pending\n',
            encoding="utf-8",
        )
        result = current_stage_summary(self.root)
        self.assertEqual(result["trace_id"], "OPP-2026-001")
        self.assertEqual(result["current_stage"], "proposal")
        self.assertEqual(result["next_stage"], "deal_gate")
        self.assertEqual(result["total_stages"], 17)

    def test_progress_summary_fallback_recognizes_presales(self):
        # 无 progress.yaml 时，产物扫描能识别售前阶段产物
        (self.root / "商机档案-2026-07-10.md").write_text("# 商机档案", encoding="utf-8")
        (self.root / "报价单-2026-07-12.md").write_text("# 报价单", encoding="utf-8")
        # 移除下游产物，确保推断停在售前
        (self.root / "stories" / "story-a.md").unlink()
        (self.root / "stories").rmdir()
        (self.root / "_映射表.json").unlink()
        (self.root / "客户确认记录-2026-07-31.md").unlink()
        (self.root / "技术就绪-readiness.md").unlink()
        (self.root / "验收报告-2026-07-31.md").unlink()
        (self.root / "评测报告-2026-07-31.md").unlink()
        result = current_stage_summary(self.root)
        self.assertEqual(result["source"], "inferred-from-files")
        self.assertEqual(result["current_stage"], "proposal")


if __name__ == "__main__":
    unittest.main()
