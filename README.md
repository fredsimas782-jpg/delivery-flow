# delivery-flow — 交付型敏捷 AI 研发工作流

> 一套**可安装、可复制、能脱离个人独立运转**的团队交付流水线。
> 任何角色（产品经理 / 项目经理 / 研发）装上本插件后，全员按同一条流水线走。
> 本仓库是**通用层**，不含任何具体项目内容；项目特定约束只放在消费方项目根的 `project-context.md`。

## 它解决什么

需求接入 → 分析 → PRD → 产品设计 → 原型 → **客户签字** → 拆任务进飞书 → 敏捷研发 → **AI 评测** → 测试 → **客户验收**。全程有依据、有关卡。

## 轻量模式（本模块的定位取舍）

对小团队/单项目，**BMAD 只当"前端文档工具箱"**——用它的 PRD/story 模板与角色 agent 产文档。**不启用** BMAD 的 sprint-status、多 agent 重交接、correct-course 重流程。**执行状态的唯一真源在飞书**，避免两套状态源打架。

## 分层设计（只建市面上没有的）

```
Layer0 基座（安装，不自建）
  ├─ BMAD-METHOD v6  文档工具箱：角色 agent + PRD/story 模板 + project-context 生成
  └─ Superpowers      研发内功：TDD / 系统化调试 / 写计划 / 验证

Layer1 本模块四个差异化关卡（BMAD 没有、必须自建）
  ├─ delivery-client-gate      入口：客户签字关卡（未签字不进开发）
  ├─ delivery-feishu-sync      拆任务：故事 → 飞书「清单>父任务>子任务」，飞书=执行真源
  ├─ delivery-eval-loop        AI 评测内循环（Tier1 引用覆盖/引用忠实/拒答正确→达阈值放行；Tier2 需专家）
  └─ delivery-acceptance-gate  出口：客户验收关卡（对着签字范围核对 KPI/DoD，取得验收签字）

Layer2 上手编排（"装上就跑"入口）
  └─ delivery-onboarding   识别角色 → 确保基座就位 → 发放角色依据 → 路由到对应阶段
```

## 与 BMAD 的分工（不重造轮子）

| 能力 | 由谁提供 |
|---|---|
| 角色 agent（分析/PM/UX 等）+ PRD/story 模板 | BMAD（当文档工具箱用）|
| 项目宪法（AI 必守规则）| BMAD `generate-project-context` → `project-context.md` |
| 研发内功（TDD/调试/验证）| Superpowers |
| **客户签字关卡（入口）** | **本模块 delivery-client-gate** |
| **飞书任务 SSOT 同步（飞书=执行真源）** | **本模块 delivery-feishu-sync**（编排 lark-* skills）|
| **AI 输出评测内循环** | **本模块 delivery-eval-loop** |
| **客户验收关卡（出口）** | **本模块 delivery-acceptance-gate** |

> 轻量模式下**不启用** BMAD 的 sprint-status / 多 agent 交接 / correct-course——这些对小团队过重。变更走 client-gate 重签即可。

## 安装

见 `.claude-plugin/marketplace.json`。消费方项目需先安装 BMAD v6 与 Superpowers（delivery-onboarding 会检测并提示）。

📖 **分步安装与上手指引** → 详见 [`docs/安装与上手.md`](docs/安装与上手.md)。含安装命令、角色分工表、端到端示例流程。

## 实例层（换项目只换这个）

项目特定的预算/技术红线/技术栈/性能验收线/风险防线 —— 全部放在**消费方项目根的 `project-context.md`**。本模块提供两份实例层占位模板：

- `templates/project-context模板.md` —— **面向 AI Agent 注入**的机读版（带 frontmatter）。复制到消费方项目根改名 `project-context.md`，或直接跑 BMAD `bmad-generate-project-context` 交互生成。
- `templates/项目宪法模板.md` —— **面向人读**的项目治理文档（一句话项目/预算模块边界/RACI 式团队规则）。
