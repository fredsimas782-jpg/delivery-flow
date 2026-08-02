---
name: delivery-trace
description: 只读检查 SPEC、Story、飞书映射、评测和验收之间的产物追溯链。当用户说“追溯需求”“检查上下文链”“delivery trace”时使用。
---

# 交付产物追溯（delivery-trace）

调用本地 `delivery trace --json` 输出从 SPEC Capability / Success signal 到 Story、飞书 task_id、评测和验收证据的链路摘要。

只报告缺链、重复 ID、悬空映射和漂移，不自动补链、不自动生成证据、不调用飞书。
