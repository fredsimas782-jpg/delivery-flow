# Changelog

## v0.1.0 (2026-07-24)

### Added

- **插件从首个消费方项目剥离为独立可安装插件**：完成通用化剥离，所有项目特定内容移入消费方 `project-context.md`
- **4 个差异化关卡 skill** 完整可用，并新增两项流程编排能力：
  - `delivery-client-gate`：客户签字关卡（A 新确认 / B 存量登记 / C 变更确认三入口）
  - `delivery-feishu-sync`：飞书任务 SSOT 同步（三层结构：清单→父任务→子任务）
  - `delivery-sprint-sync`：飞书状态单向同步到本地 `sprint-status.yaml` 只读镜像
  - `delivery-eval-loop`：AI 评测内循环（Tier1 引用覆盖/忠实/拒答 → 门禁放行；Tier2 答案正确/检索命中 → 待专家）
  - `delivery-acceptance-gate`：客户验收关卡（验收依据 = client-gate 冻结快照）
  - `delivery-prototype-html`：从 SPEC / PRD / UX 产出可离线运行的全页面交互原型
- **入口编排** `delivery-onboarding`：角色识别 → 基座检测 → 路由到阶段
- **4 份关卡模板**：客户确认记录、评测集、评测报告、验收报告（含 Tier1/Tier2 分层、自检清单）
- **实例层占位模板**：`project-context模板.md`（AI Agent 注入）、`项目宪法模板.md`（人读治理）

### Changed

- 全插件统一 `"version": "0.1.0"`

---

此版本是 delivery-flow 的初始发布版本，包含：
- 7 个 Skill：4 个乙方交付关卡、HTML 原型、飞书状态镜像、入口编排
- 关卡模板、实例层模板、上手文档、映射表、示范样例和 6 份 ADR
- `.claude-plugin/plugin.json` 已声明 BMAD-METHOD、Superpowers 必需依赖和 lark 技能可选依赖

### 能力边界

- 本仓库提供 Markdown Skill、模板和示范文档，不包含运行时执行脚本、飞书 API 封装、评测 runner 或自动门禁。
- 飞书操作依赖外部 `lark-*` 技能；BMAD 安装命令仍需在真实消费方项目中验证。
- 后续重点是自动化执行、测试和真实集成验证，不是继续重复 BMAD 或 Superpowers 已有能力。
