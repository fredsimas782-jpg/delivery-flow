---
name: delivery-bootstrap
description: 从零把新项目装到 delivery-flow 就绪状态：自动检测当前 AI 工具（Claude Code / Codex / Cursor / Windsurf 等）、支持 GitHub URL 直接安装、生成对应配置文件、安装 BMAD/Superpowers、创建 project-context.md 和 project-progress.yaml，完成后交接给 delivery-onboarding。当用户说"装 delivery-flow"、"初始化项目"、"bootstrap"、"从零开始装插件"、"新项目安装"时使用。
---

# delivery-flow 安装引导（delivery-bootstrap）

**目标**：让一个从未接触过 delivery-flow 的用户，在新电脑/新项目上从零完成环境搭建，无论使用 Claude Code、Codex、Cursor 还是 Windsurf，都能自动适配。

**角色**：你是安装秘书。按清单逐步检查、修复、创建，不替用户做业务决策，但可以问必要的配置问题。

## 何时用

- 用户在新项目中首次安装 delivery-flow
- 用户说"装 delivery-flow""从零开始""bootstrap"
- 项目缺少关键依赖文件（`_bmad/`、`project-context.md`、delivery-flow 配置文件）

## 不何时用

- 项目已安装完毕，用户只是想进入工作流 → 直接用 `delivery-onboarding`
- 项目已有 `project-progress.yaml` 且各阶段在推进 → 不需要重新 bootstrap

## 支持的工具

| 工具 | 配置文件 | 说明 |
|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` | 原生插件系统 |
| Codex (OpenAI) | `AGENTS.md` | 项目级指令文件 |
| Cursor | `.cursor/rules/delivery-flow.mdc` | Rules 规则文件 |
| Windsurf | `.windsurf/rules/delivery-flow.md` | Rules 规则文件 |
| 其他工具 | `docs/跨工具安装指南.md` | 手动步骤 |

## 全局原则

1. **只做安装，不做业务决策**——项目红线、验收标准等内容让用户自己填，bootstrap 只负责搭脚手架。
2. **每步有明确的成功判定**——不靠"大概装好了"，必须看到具体文件/目录/配置项才算完成。
3. **失败可恢复**——任何一步失败都不阻断后续检查，最后汇总报告哪些成功、哪些需要手动处理。
4. **幂等**——重复执行不会创建重复文件、不会覆盖用户已填好的内容。

<workflow>

<step n="1" goal="环境预检与工具检测">
  <action>检查当前目录是否有 `.git/` 目录——判断是否在 git 仓库内。记录仓库根目录路径。</action>
  <check if="不在 git 仓库内">
    <action>提示用户："建议在项目根目录初始化 git（`git init`），delivery-flow 的很多产物需要 git 追踪。是否现在初始化？"如用户同意则执行 `git init`。</action>
  </check>
  <action>**检测当前 AI 工具**，按优先级依次判断：</action>
  <action>1. 检查 `.claude-plugin/` 目录是否存在 → 是则标记为 **Claude Code**</action>
  <action>2. 检查 `AGENTS.md` 是否存在于项目根 → 是则标记为 **Codex**</action>
  <action>3. 检查 `.cursor/` 目录是否存在 → 是则标记为 **Cursor**</action>
  <action>4. 检查 `.windsurf/` 目录是否存在 → 是则标记为 **Windsurf**</action>
  <action>5. 以上都不存在 → 询问用户当前使用的工具，或标记为 **其他**</action>
  <action>记录检测结果：工具类型 + 项目根目录路径，后续步骤据此生成对应配置。</action>
</step>

<step n="2" goal="获取 delivery-flow 来源">
  <action>按优先级尝试获取 delivery-flow：</action>
  <action>1. **检查项目配置文件是否已引用 delivery-flow**：根据 step 1 检测到的工具，读取对应配置文件（`.claude-plugin/marketplace.json` / `AGENTS.md` / `.cursor/rules/` / `.windsurf/rules/`），看是否已包含 delivery-flow 相关内容。若有，记录来源路径，跳到 step 3。</action>
  <action>2. **检查当前仓库的 git remote**：执行 `git remote -v`，如果输出包含 `delivery-flow`，说明用户就在 delivery-flow 仓库本身——此时提醒："你正在 delivery-flow 仓库内，请切换到你的消费项目目录后重新运行"，停止后续步骤。</action>
  <action>3. **询问用户**：以上都不满足时，问用户——"请提供 delivery-flow 的来源：(a) GitHub 地址 如 `https://github.com/fredsimas782-jpg/delivery-flow.git` (b) 本地路径 如 `D:/code/delivery-flow` (c) 我帮你从 GitHub clone 一份"</action>
  <check if="用户提供了 GitHub URL（无论是否选了 c）">
    <action>在用户指定位置（默认 `~/delivery-flow`）执行 `git clone <URL>`，完成后记录本地路径。如用户未指定位置，询问"clone 到哪里？默认 `~/delivery-flow`"。</action>
  </check>
  <action>验证来源路径下存在 `skills/` 目录和 `templates/` 目录——确认是有效的 delivery-flow 仓库。</action>
  <check if="验证失败">
    <action>提示："该路径下未找到 `skills/` 目录，可能不是有效的 delivery-flow 仓库。请确认路径后重试。"回退到询问步骤。</action>
  </check>
</step>

<step n="3" goal="注册 delivery-flow 到消费项目（按工具类型生成配置）">
  <action>根据 step 1 检测到的工具类型，执行对应的配置生成：</action>

  <check if="工具 = Claude Code">
    <action>检查项目根是否存在 `.claude-plugin/marketplace.json`。</action>
    <check if="文件不存在">
      <action>创建 `.claude-plugin/` 目录和 `marketplace.json`：</action>
      <action>
```json
{
  "name": "<项目名>-marketplace",
  "plugins": [
    {
      "name": "delivery-flow",
      "source": "<step2 中获取的路径>"
    }
  ]
}
```
      </action>
    </check>
    <check if="文件已存在但没有 delivery-flow 条目">
      <action>读取现有 `marketplace.json`，在 `plugins` 数组中追加 delivery-flow 条目。保留已有条目不动。</action>
    </check>
    <check if="文件已存在且已有 delivery-flow 条目">
      <action>跳过，提示"delivery-flow 已注册"。</action>
    </check>
  </check>

  <check if="工具 = Codex">
    <action>在项目根创建或更新 `AGENTS.md`，追加以下内容（不覆盖已有内容）：</action>
    <action>
```
## delivery-flow 交付工作流

delivery-flow 已安装，技能文件位于 `<delivery-flow 路径>/skills/`。
当需要执行交付流程时，按以下顺序读取并遵循对应 SKILL.md：
- `delivery-bootstrap` — 安装引导（首次使用）
- `delivery-onboarding` — 流程入口与角色路由
- `delivery-client-gate` — 客户签字关卡
- `delivery-feishu-sync` — 飞书任务同步
- 其余技能见 `<delivery-flow 路径>/skills/` 目录

项目约束文件：`project-context.md`（必须存在）
阶段进度文件：`project-progress.yaml`
```
    </action>
  </check>

  <check if="工具 = Cursor">
    <action>创建 `.cursor/rules/` 目录（如不存在），写入 `delivery-flow.mdc`：</action>
    <action>
```
---
description: delivery-flow 交付工作流指令
globs: ["**/*.md", "**/*.yaml"]
---

# delivery-flow 交付工作流

delivery-flow 已安装，技能文件位于 `<delivery-flow 路径>/skills/`。
当需要执行交付流程时，按以下顺序读取并遵循对应 SKILL.md：
- `delivery-bootstrap` — 安装引导（首次使用）
- `delivery-onboarding` — 流程入口与角色路由
- `delivery-client-gate` — 客户签字关卡
- `delivery-feishu-sync` — 飞书任务同步
- 其余技能见 `<delivery-flow 路径>/skills/` 目录

项目约束文件：`project-context.md`（必须存在）
阶段进度文件：`project-progress.yaml`
```
    </action>
  </check>

  <check if="工具 = Windsurf">
    <action>创建 `.windsurf/rules/` 目录（如不存在），写入 `delivery-flow.md`：</action>
    <action>
```
# delivery-flow 交付工作流

delivery-flow 已安装，技能文件位于 `<delivery-flow 路径>/skills/`。
当需要执行交付流程时，按以下顺序读取并遵循对应 SKILL.md：
- `delivery-bootstrap` — 安装引导（首次使用）
- `delivery-onboarding` — 流程入口与角色路由
- `delivery-client-gate` — 客户签字关卡
- `delivery-feishu-sync` — 飞书任务同步
- 其余技能见 `<delivery-flow 路径>/skills/` 目录

项目约束文件：`project-context.md`（必须存在）
阶段进度文件：`project-progress.yaml`
```
    </action>
  </check>

  <check if="工具 = 其他">
    <action>提示用户："当前工具未在自动适配范围内。请参考 `delivery-flow/docs/跨工具安装指南.md` 手动配置。核心步骤：(1) 将 delivery-flow 的 `skills/` 目录路径告知 AI agent (2) 在项目中创建 `project-context.md`。"</action>
  </check>

  <action>**验证**：根据工具类型，重新读取对应配置文件，确认 delivery-flow 条目存在且路径可访问。</action>
</step>

<step n="4" goal="安装 BMAD-METHOD v6">
  <action>检查项目根是否存在 `_bmad/` 目录。</action>
  <check if="_bmad/ 已存在">
    <action>跳过，提示"BMAD 已安装"。检查 `_bmad/` 下是否有 `core/` 或 `agents/` 子目录，确认安装完整。</action>
  </check>
  <check if="_bmad/ 不存在">
    <action>执行 `npx bmad-method install`。</action>
    <check if="执行成功">
      <action>验证 `_bmad/` 目录已创建。成功则记录 ✅。</action>
    </check>
    <check if="执行失败或报错">
      <action>提示用户："BMAD 自动安装未成功（此命令在部分空白项目上可能有问题）。请手动处理：(1) 查阅 BMAD-METHOD 官方文档获取最新安装方式 (2) 安装完成后确认项目根有 `_bmad/` 目录 (3) 然后告诉我'BMAD 已装好'继续。"**不阻断流程**——继续后续步骤，但最终报告中标记 BMAD 为"需手动完成"。</action>
    </check>
  </check>
</step>

<step n="5" goal="安装 Superpowers">
  <action>检查 Superpowers 是否已注册。</action>
  <check if="工具 = Claude Code">
    <action>查看 `.claude-plugin/marketplace.json` 的 `plugins` 数组是否包含 `name: "superpowers"` 或 `source` 含 `obra/superpowers`。已注册则跳过；未注册则追加 `{ "name": "superpowers", "source": "obra/superpowers" }`。</action>
  </check>
  <check if="工具 = Codex / Cursor / Windsurf">
    <action>在对应配置文件（AGENTS.md / .cursor/rules/delivery-flow.mdc / .windsurf/rules/delivery-flow.md）中追加一行："研发内功基座：Superpowers（obra/superpowers），提供 TDD / 系统化调试 / 验证能力。如已安装请忽略。"</action>
  </check>
  <check if="工具 = 其他">
    <action>提示用户："Superpowers 是可选的研发内功基座（TDD/调试/验证），如需要请参考 `obra/superpowers` 安装说明配置。当前不影响核心流程使用。"</action>
  </check>
</step>

<step n="6" goal="检测飞书技能（可选，仅提示）">
  <action>列出已安装的 skill 名称，检查是否包含 `lark-task`、`lark-base` 或其他 `lark-*` 技能。</action>
  <check if="有 lark-* 技能">
    <action>记录"飞书技能已就位"。后续 onboarding 中如涉及飞书同步会用到。</action>
  </check>
  <check if="没有 lark-* 技能">
    <action>提示："飞书技能（lark-task / lark-base 等）未检测到。如项目需要推任务到飞书，请后续按 lark-* 技能的安装说明配置。当前不影响非飞书环节的使用。"**不阻断流程**。</action>
  </check>
</step>

<step n="7" goal="创建 project-context.md">
  <action>检查项目根是否存在 `project-context.md`。</action>
  <check if="已存在">
    <action>跳过，提示"project-context.md 已存在，不覆盖"。读取 frontmatter，报告已填字段数/空字段数。</action>
  </check>
  <check if="不存在">
    <action>采用交互方式，依次询问用户以下关键字段（其余字段留占位符）：</action>
    <action>1. **项目名称**（用于 frontmatter 和文件内引用）</action>
    <action>2. **技术栈**：后端框架+版本、前端框架+版本、部署平台</action>
    <action>3. **AI 能力边界**：只做集成还是含训练？用哪家大模型 API？</action>
    <action>4. **技术红线**：列出 1-3 条最重要的"不做"事项</action>
    <action>5. **验收指标**：性能指标+阈值（其他指标留占位符，用户后续填）</action>
    <action>将用户回答填入 delivery-flow 的 `templates/project-context模板.md` 的对应 `{{}}` 占位符，其余未回答的字段保留占位符。输出到项目根，文件名 `project-context.md`。</action>
    <action>告知用户："已创建 project-context.md，填充了你提供的信息。其余占位符（标注 `{{}}` 的部分）请在正式开始工作前补全。这是 AI Agent 的'宪法级'注入文件，违反其中红线会导致返工。"</action>
  </check>
</step>

<step n="8" goal="初始化 project-progress.yaml">
  <action>检查项目根是否存在 `project-progress.yaml`。</action>
  <check if="已存在">
    <action>跳过，提示"project-progress.yaml 已存在"。读取 `current_stage`，报告当前进度。</action>
  </check>
  <check if="不存在">
    <action>从 delivery-flow 的 `templates/project-progress模板.yaml` 复制到项目根。将所有阶段的 `status` 改为 `pending`，`completed_at`/`started_at`/`gate_evidence` 字段删除，`current_stage` 设为 `requirements`，`project` 设为 step 7 中用户提供的项目名。</action>
  </check>
</step>

<step n="9" goal="汇总报告与交接">
  <action>输出安装结果汇总表：</action>
  <action>| 检查项 | 状态 | 备注 |</action>
  <action>| 当前工具 | — | 检测到: {工具类型} |</action>
  <action>| git 仓库 | ✅/⚠️ | ... |</action>
  <action>| delivery-flow 来源 | ✅ | 路径: ... |</action>
  <action>| 工具配置文件 | ✅/⚠️ | {对应文件名} |</action>
  <action>| BMAD | ✅/⚠️ | ... |</action>
  <action>| Superpowers | ✅/⚠️ | ... |</action>
  <action>| 飞书技能 | ✅/跳过 | ... |</action>
  <action>| project-context.md | ✅/⚠️ | 已填 N/M 字段 |</action>
  <action>| project-progress.yaml | ✅ | current_stage: requirements |</action>
  <check if="所有项为 ✅">
    <action>提示："安装完成！现在可以开始使用 delivery-flow 了。说 **'我该做什么'** 即可进入 delivery-onboarding，它会帮你识别角色、定位阶段、开始工作。"</action>
  </check>
  <check if="有 ⚠️ 项">
    <action>先逐一说明每个 ⚠️ 项的手动处理方式，再提示处理完后说"继续"或"我该做什么"来触发 delivery-onboarding。</action>
  </check>
</step>

</workflow>

## 与 delivery-onboarding 的关系

- **bootstrap 做的事**：环境检查 → 注册插件 → 安装依赖 → 创建初始文件 → 报告
- **onboarding 做的事**：检查基座就位（重新验证）→ 识别角色 → 定位当前阶段 → 路由到对应 skill
- bootstrap 完成后，onboarding 的 step 1（基座检查）会自动通过，直接进入 step 2（角色识别）
- **不重复检查**：bootstrap 创建了 `project-progress.yaml` 后，onboarding 直接读它定位阶段，跳过产物扫描

## 作为开源插件分发

delivery-flow 设计为可独立分发的开源插件：

```
# 任何工具的用户，三步开始：
git clone https://github.com/fredsimas782-jpg/delivery-flow.git
cd <你的项目>
# 然后用你的 AI 工具说"装 delivery-flow"或参考 安装指南.md
```

- **Claude Code 用户**：说"装 delivery-flow"，bootstrap 自动引导
- **其他工具用户**：打开 `安装指南.md`，按工具类型找到对应安装步骤
