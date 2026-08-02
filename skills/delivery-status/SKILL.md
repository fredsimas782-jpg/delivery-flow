---
name: delivery-status
description: 只读聚合本地 sprint-status.yaml 镜像并报告状态。当用户说“查看交付状态”“汇总 sprint”“delivery status”时使用。
---

# 交付状态只读汇总（delivery-status）

调用本地 `delivery status --json` 读取本地状态镜像，汇总任务数量、状态和阻塞项。

飞书是执行状态真源；本地状态只读，禁止由本 Skill 写回飞书、刷新飞书或改变需求文档。
