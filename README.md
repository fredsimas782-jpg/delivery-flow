# delivery-flow — 交付型敏捷 AI 研发工作流

> 一套**可安装、可复制、能脱离个人独立运转**的团队交付流水线。
> 任何角色（产品经理 / 项目经理 / 研发）装上本插件后，全员按同一条流水线走。
> 本仓库是**通用层**，不含任何具体项目内容；项目特定约束只放在消费方项目根的 `project-context.md`。

## 它解决什么

需求接入 → BMAD 分析立项 → SPEC / PRD / UX → HTML 原型 → **客户签字** → 架构 / 技术就绪 → Story 拆解进飞书 → Superpowers 研发 → **AI 评测** → 测试 → **客户验收**。全程有依据、有关卡。`project-progress.yaml` 持久化记录当前所处阶段，由关卡 skill 自动写入。

## 标准模式（本模块的定位）

**BMAD 的产品与规划能力全开**：分析研究、SPEC、PRD、UX、架构、技术就绪检查和 Story 拆解都优先复用 BMAD。**Superpowers** 负责研发阶段的 TDD、调试和验证。飞书是执行状态唯一写端，本地 `sprint-status.yaml` 仅由 `delivery-sprint-sync` 从飞书单向拉取，作为只读镜像。

本仓库提供的是 Markdown 工作流规范、模板和角色路由，不是带运行时代码的项目管理系统；飞书 API、评测执行器和自动门禁依赖外部技能或人工执行。

## 分层设计（只建市面上没有的）

```
Layer0 基座（安装，不自建）
  ├─ BMAD-METHOD v6  文档工具箱：角色 agent + PRD/story 模板 + project-context 生成
  └─ Superpowers      研发内功：TDD / 系统化调试 / 写计划 / 验证

Layer1 本模块差异化交付能力（补 BMAD 未覆盖的业务关卡与编排）
  ├─ delivery-client-gate      入口：客户签字关卡（未签字不进开发）
  ├─ delivery-feishu-sync      拆任务：故事 → 飞书「清单>父任务>子任务」，飞书=执行真源
  ├─ delivery-sprint-sync       状态镜像：飞书 → 本地 sprint-status.yaml（只读）
  ├─ delivery-eval-loop        AI 评测内循环（Tier1 达阈值放行；Tier2 需专家）
  ├─ delivery-acceptance-gate  出口：客户验收关卡（对签字范围核 KPI/DoD）
  └─ delivery-prototype-html    规划编排：将 BMAD UX 产物转为可交互 HTML 演示原型

Layer2 上手编排（”装上就跑”入口）
  ├─ delivery-bootstrap    从零安装：环境检查 → 注册插件 → 装依赖 → 创建初始文件
  └─ delivery-onboarding   识别角色 → 确保基座就位 → 发放角色依据 → 路由到对应阶段
```

## 与 BMAD 的分工（不重造轮子）

| 能力 | 由谁提供 |
|---|---|
| 角色 agent（分析/PM/UX 等）+ SPEC / PRD / Story 模板 | BMAD |
| 项目宪法（AI 必守规则）| BMAD `generate-project-context` → `project-context.md` |
| 研发内功（TDD/调试/验证）| Superpowers |
| **客户签字关卡（入口）** | **本模块 delivery-client-gate** |
| **飞书任务 SSOT 同步（飞书=执行真源）** | **本模块 delivery-feishu-sync**（编排 lark-* skills）|
| **飞书状态本地只读镜像** | **本模块 delivery-sprint-sync** |
| **HTML 交互原型编排** | **本模块 delivery-prototype-html**（读取 bmad-ux 产物）|
| **AI 输出评测内循环** | **本模块 delivery-eval-loop** |
| **客户验收关卡（出口）** | **本模块 delivery-acceptance-gate** |
| **从零安装引导** | **本模块 delivery-bootstrap** |

> BMAD 的产品与规划能力全开；`sprint-status.yaml` 不作为本地写端，仅由 `delivery-sprint-sync` 从飞书单向刷新。

## 安装

> **最快方式**：在 Claude Code 中说 **"装 delivery-flow"** 或 **"bootstrap"**，`delivery-flow` 会自动引导完成环境搭建，无需手动查阅文档。

📖 **快速安装指南** → 详见 [`安装指南.md`](安装指南.md)。含 Claude Code 一键安装和其他工具（Codex / Cursor / Windsurf）分步指引。

📖 **分步安装与上手指引** → 详见 [`docs/安装与上手.md`](docs/安装与上手.md)。含安装命令、角色分工表、端到端示例流程。

🔧 **非 Claude Code 工具安装** → 详见 [`docs/跨工具安装指南.md`](docs/跨工具安装指南.md)。Codex / Cursor / Windsurf 各有对应配置步骤。

### 快速开始（按工具）

**Claude Code**：在你的项目目录打开 Claude Code，说"装 delivery-flow"，自动完成全部安装。

**Codex / Cursor / Windsurf**：
```bash
# 1. clone 本仓库
git clone https://github.com/fredsimas782-jpg/delivery-flow.git

# 2. 进入你的项目，安装 BMAD
cd <你的项目>
npx bmad-method install

# 3. 让 AI 帮你创建配置文件（参考 docs/跨工具安装指南.md）
```

## 日常使用

装好之后，按以下流程推进项目：

```
1. 说"我该做什么"        → AI 识别你的角色，告诉你当前该做哪一步
2. 按提示执行对应工作     → 每一步都有对应的 skill 引导
3. 完成后说"下一步"       → AI 自动推进到下一阶段
```

**关键节点（硬门禁，不可跳过）**：

| 节点 | 谁触发 | 说明 |
|---|---|---|
| 客户签字 | 项目经理 | 未签字不进开发 |
| 技术就绪检查 | 架构师/技术 Lead | 不达标不拆任务 |
| AI 评测 | AI 工程师 | Tier1 不达标不进测试 |
| 客户验收 | 项目经理 | 未验收不算交付完成 |

**各角色日常入口**：

| 角色 | 在 AI 工具中说 | 进入的流程 |
|---|---|---|
| 产品经理 | "我是产品经理" | 分析立项 → PRD → UX → HTML原型 |
| 项目经理 | "我是项目经理" | 客户签字 → 拆任务 → 跟进 → 验收 |
| 研发工程师 | "我是研发" | 从飞书领任务 → TDD 开发 → 自测 |
| AI 工程师 | "我是AI工程师" | 跑评测 → 出报告 |

## 实例层（换项目只换这个）

项目特定的预算/技术红线/技术栈/性能验收线/风险防线 —— 全部放在**消费方项目根的 `project-context.md`**。本模块提供两份实例层占位模板：

- `templates/project-context模板.md` —— **面向 AI Agent 注入**的机读版（带 frontmatter）。复制到消费方项目根改名 `project-context.md`，或直接跑 BMAD `bmad-generate-project-context` 交互生成。
- `templates/项目宪法模板.md` —— **面向人读**的项目治理文档（一句话项目/预算模块边界/RACI 式团队规则）。
