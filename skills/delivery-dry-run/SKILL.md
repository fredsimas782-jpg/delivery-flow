---
name: delivery-dry-run
description: 预览推送飞书的任务计划但不联网、不写文件。当用户说“预演推飞书”“dry run”“预览任务”时使用。
---

# 飞书任务预演（delivery-dry-run）

调用本地 `delivery dry-run --json` 读取 stories、SPEC 和映射表，输出将创建、更新或跳过的任务计划。

本 Skill 严格无副作用：不调用网络、不写入映射表、不创建或更新飞书任务、不刷新本地状态。已有映射只能 update 或 skip，不得盲目创建。
