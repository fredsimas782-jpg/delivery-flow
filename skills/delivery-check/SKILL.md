---
name: delivery-check
description: 只读检查交付项目的产物完整性、阶段前置条件和关卡证据。当用户说“检查交付流程”“检查项目状态”“delivery check”时使用。
---

# 交付一致性检查（delivery-check）

调用本地 `delivery check --json` 读取项目文件并报告问题，不修改任何文件、不调用飞书、不替代客户或专家判断。

重点检查：SPEC 五字段、客户确认、技术就绪、Story 三要素、映射表结构、评测和验收证据，以及后段产物是否绕过前置关卡。

`fail` 或 `unknown` 都不能解释为通过。真人签字、Tier2 专家结论和技术取舍必须由对应角色确认。
