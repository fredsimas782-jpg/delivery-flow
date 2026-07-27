---
name: delivery-onboarding
description: 交付流水线的总入口与角色路由器。新成员装上插件后首启：识别角色→确保基座就位→发放该角色的工作依据→路由到当前该做的阶段。当用户说"我加入了"、"我该做什么"、"开始工作流"、"delivery start"、"角色路由"时使用。
---

# 交付流水线入口 / 角色路由（delivery-onboarding）

**目标**：让任何角色（产品经理 / 项目经理 / 研发 / AI 工程师）装上插件后，**不依赖某个人**就能上手：知道自己在流水线哪一环、依据什么干活、下一步调哪个 skill。

**角色**：你是流程引导员。不替用户干活，而是把他领到正确的阶段和工具。

## 轻量模式（本模块的定位）

BMAD 在此**只当"前端文档工具箱"**——用它的 PRD/story 模板与角色 agent 产文档。**不启用** BMAD 的 sprint-status、多 agent 重交接、correct-course 重流程。**执行状态真源在飞书**。这样对小团队/单项目最省。

## 全景流水线（谁在哪一环）

```
需求接入→分析→PRD→产品/原型→[客户签字]→拆任务进飞书→敏捷研发→[AI评测]→测试→[客户验收]
   PM     PM   PM    UX        项目经理      项目经理        研发       AI工程师  QA     项目经理
```

方括号 = 本模块补 BMAD 之缺的**四个关卡**（入口签字 / 飞书SSOT / AI评测 / 出口验收）。其余走 BMAD 文档工具。

## 角色 → 依据 → 阶段 → 工具

| 角色 | 工作依据 | 主责阶段 | 调用 |
|---|---|---|---|
| 产品经理 | 需求原文 + `project-context.md`(红线) | 分析→PRD→原型 | `bmad-agent-analyst`、`bmad-prd`、`bmad-ux` |
| 项目经理 | 已签字 PRD/原型 | 客户确认→拆任务→跟进→验收 | `delivery-client-gate`、`bmad-create-epics-and-stories`、`delivery-feishu-sync`、`delivery-acceptance-gate` |
| 研发工程师 | **飞书子任务 + story 的 AC** | 敏捷研发 | 从飞书领活 → Superpowers（TDD/调试/验证）实现自测 → 改飞书阶段状态 |
| AI 工程师 | stories/AC + 阈值 | AI 评测 | `delivery-eval-loop` |

> 变更（轻量）：客户签字后要改范围 → 更新 `客户确认记录`、回 client-gate 重签即可，不上 BMAD 重流程。

<workflow>

<step n="1" goal="确保基座就位">
  <action>检查 BMAD 是否装（项目根有 `_bmad/`）——用作文档工具箱。缺则提示 `npx bmad-method install`。</action>
  <action>检查 Superpowers 是否装（研发角色必需，保证 TDD/调试/验证一致性）。缺则提示装 obra/superpowers。</action>
  <action>检查 `project-context.md`（实例层：红线/阈值/验收线）是否存在。缺则提示跑 `bmad-generate-project-context` 或用本模块 `templates/project-context模板.md` 填。</action>
  <action if="涉及飞书">确认 lark-* skill 可用且已授权（领活/推任务需要）。</action>
</step>

<step n="2" goal="识别角色">
  <action>问："你是哪个角色？产品经理 / 项目经理 / 研发 / AI 工程师？"（或从自述判断）</action>
  <action>发放该角色的「工作依据」——明确告诉他干活的凭据是什么，不凭空发挥。</action>
</step>

<step n="3" goal="定位当前阶段">
  <action>扫产物判断走到哪。**先滤噪声**：名含"模板"/template、或路径含 `skills/`、`_bmad/`、`.agents/`、`.claude/` 的都是模板或 skill 资产，不算真实产物（否则会被 `xx-PRD模板.md`、`prd-template.md` 骗）。</action>
  <action>按流水线顺序查真实产物：PRD → 原型/UX → 客户确认记录 → 飞书映射/任务 → 评测报告 → 验收报告。正常情况找"最后一个已完成阶段"，下一环即当前动作。</action>
  <action>**检测乱序/不一致**（真实项目常见，尤其 delivery-flow 引入前已有存量工作）：若某后段产物存在、但其前置关卡产物缺失（典型：飞书已有任务却无客户确认记录），**不要假装线性推进**——明确标出不一致，提示补齐前置关卡后再继续。</action>
  <action>**缺客户确认记录时先问，别急着让人重签**：客户是否已通过别的形式确认过范围（往返确认的甲方原始材料 / 确认邮件 / 会议纪要）？是 → 走 `delivery-client-gate` 的 **B 入口**登记既有确认（不重签）；否 → 走 A 入口组织签字。</action>
  <action>结合角色与 `project-context.md` 的外部约束（如 PoC/前置输入未就绪），告诉用户"当前该你做的是哪一环"，必要时点明外部阻塞。</action>
</step>

<step n="4" goal="路由">
  <action>按上表导向对应 skill，说明其输入与产出。</action>
  <action>提醒关卡纪律（见下）。</action>
</step>

</workflow>

## 关卡纪律（团队共识，靠自觉不靠技术锁）

> 诚实说明：这些关卡是**流程约定**，没有技术强制——任何人硬跳过也没程序拦。但跳过=破坏交付可追溯性，团队须共识遵守。

1. **客户没签字 → 不进开发**（client-gate）
2. **任务三要素不全 → 不推飞书**（feishu-sync）
3. **AI 评测 Tier1 不达阈值 → 不进 QA/上线**（eval-loop）
4. **没过客户验收 → 不算交付**（acceptance-gate）
5. 需求真源在文档、状态真源在飞书——回读飞书绝不覆盖文档正文（SSOT）

## 两步必须真人（工作流只能检测、不能代替）

- **客户签字**（client-gate 入口 / acceptance-gate 出口）：本质是甲乙双方线下动作，AI 只能生成待签件、检测是否已签。
- **eval Tier2 专家标注**：答案正确率/检索命中率需领域专家给标准答案，专家不到位则挂起，不自造答案。
