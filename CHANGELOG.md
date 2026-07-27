# Changelog

## v0.1.0 (2026-07-24)

### Added

- **插件从首个消费方项目剥离为独立可安装插件**：完成通用化剥离，所有项目特定内容移入消费方 `project-context.md`
- **4 个差异化关卡 skill** 完整可用：
  - `delivery-client-gate`：客户签字关卡（A 新确认 / B 存量登记 / C 变更确认三入口）
  - `delivery-feishu-sync`：飞书任务 SSOT 同步（三层结构：清单→父任务→子任务）
  - `delivery-eval-loop`：AI 评测内循环（Tier1 引用覆盖/忠实/拒答 → 门禁放行；Tier2 答案正确/检索命中 → 待专家）
  - `delivery-acceptance-gate`：客户验收关卡（验收依据 = client-gate 冻结快照）
- **入口编排** `delivery-onboarding`：角色识别 → 基座检测 → 路由到阶段
- **4 份关卡模板**：客户确认记录、评测集、评测报告、验收报告（含 Tier1/Tier2 分层、自检清单）
- **实例层占位模板**：`project-context模板.md`（AI Agent 注入）、`项目宪法模板.md`（人读治理）

### Changed

- 全插件统一 `"version": "0.1.0"`

---

此版本是 delivery-flow 的初始发布版本，包含：
- 4 个差异化关卡 skill + 入口编排（delivery-onboarding）
- 4 份关卡模板（客户确认记录 / 评测集 / 评测报告 / 验收报告）
- 2 份实例层占位模板（project-context / 项目宪法）
- 上手文档与安装指引（`docs/安装与上手.md`）
- 映射表模板（`_映射表模板.json`）
- 4 份示范样例（`examples/`）
- 6 份架构决策记录（`docs/adr/`）
- LICENSE（私有/未发表）

**后续可选（非 v0.1.0 缺失）**：tests/ 校验脚手架、plugin.json 基座依赖声明、git 远端与 tag、npm 分发。
