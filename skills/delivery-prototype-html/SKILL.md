---
name: delivery-prototype-html
description: 从 SPEC.md + PRD + UX 文档生成「整页可交互 HTML 演示原型」。产出物是离线可运行的完整原型（含导航/基础交互/模拟数据），用于客户签字前的演示验证和研发 UI 参考。与 bmad-ux 的静态 mock（2-4 屏）互补：bmad-ux 定视觉调子，本 skill 做全量可交互演示。当用户说"做 HTML 原型"、"原型演示"、"交互原型"、"可点击原型"、"交付原型"时使用。
---

# HTML 演示原型（delivery-prototype-html）

**目标**：在 PRD + UX 设计完成之后、客户签字之前，产出**整页可交互的 HTML 演示原型**——让客户/领导在没写代码前就能点着看、走通流程，降低确认成本；同时给研发提供比 ASCII 线框更精确的 UI 参考。

**角色**：你是原型工程师。不写后端，只做能跑的前端演示。

## 与 bmad-ux 的分工

| 维度 | bmad-ux | delivery-prototype-html（本 skill） |
|---|---|---|
| 视觉定调 | ✅ DESIGN.md（颜色/字体/圆角/组件规范） | ✅ 从 DESIGN.md 提取视觉变量 |
| 交互规范 | ✅ EXPERIENCE.md（信息架构/状态/动效/旅程） | ✅ 从 EXPERIENCE.md 提取交互逻辑 |
| 线框 | ✅ Excalidraw 线框 | ✅ 作为页面结构依据 |
| HTML 产出 | 2-4 屏**静态** mock（离线无 JS） | **全页面可交互**原型（有 JS、可导航、可点击） |
| 定位 | 视觉语言定稿 | 交互流程验证 + 客户演示 |
| 产品负责人 | bmad-ux 设计产出交付物 | 本 skill 的输入来源 |

**不替代 bmad-ux**：如果还没做过 bmad-ux，先用 bmad-ux 产出 DESIGN/EXPERIENCE，再进本 skill。本 skill 从 DESIGN/EXPERIENCE 读视觉和交互规范，**不是从零设计**。

## 输入

- `SPEC.md`（机读契约，功能范围 + Success signal 验收标准）
- PRD（`*prd*.md`，功能细节 + 字段定义 + 接口描述）
- `DESIGN.md` + `EXPERIENCE.md`（bmad-ux 产出，视觉 + 交互规范）
- 线框图（Excalidraw 或 ASCII，页面结构依据）
- `project-context.md`（红线 / 产物路径约定）

## 输出

```
prototype/
├── index.html          # 入口页
├── app.js              # 页面路由 + 交互逻辑
├── data.js             # 模拟数据（固定 mock 数据，不调真实 API）
├── styles.css          # 从 DESIGN.md 提取的视觉变量
└── pages/              # 每个页面一个子模块
    ├── page-a.js
    ├── page-b.js
    └── ...
```

**输出目录路径**：优先读 `project-context.md` 中的产物路径约定；未指定则默认 `prototype/`（与 planning_artifacts 同级）。

## 质量标准（放行门槛）

- ✅ **离线可运行**：双击 `index.html` 能在浏览器打开，不依赖后端 / 不联网
- ✅ **全页面可导航**：每个页面都能从菜单/按钮进入，不是孤立页面
- ✅ **核心交互可点跑**：按钮点击 / 表单填写 / 列表翻页等核心路径有 JS 响应（用模拟数据）
- ✅ **视觉对齐 DESIGN.md**：颜色 / 字体 / 圆角 / 间距从 DESIGN.md 提取，不自由发挥
- ✅ **页面数量**：覆盖 SPEC.md Capabilities 的每个功能入口 + 关键交互页面（通常 6-12 页，视产品复杂度）
- ❌ **不做的事**：真实 API 调用 / 后端逻辑 / 登录鉴权 / 数据持久化 / 响应式适配（原型阶段桌面优先）

## 依赖

- SPEC.md + PRD + DESIGN.md + EXPERIENCE.md（上阶段产物）
- `project-context.md`（产物路径约定）

## 何时用

- PRD + bmad-ux（DESIGN/EXPERIENCE）已完成，进入客户签字之前
- 客户/领导需要"点着看"的演示材料，而非文档
- 研发需要比线框更精确的 UI 参考

## 工作流

<step n="1" goal="读输入">

<action>读 SPEC.md 的 Capabilities + Success signal，列出需要原型覆盖的功能模块。</action>

<action>读 DESIGN.md（颜色 / 字体 / 圆角 / 组件样式）→ 提取 CSS 变量。</action>

<action>读 EXPERIENCE.md（信息架构 / 页面路由 / 核心交互 / 用户旅程）→ 提取页面清单和交互逻辑。</action>

<action>读 PRD（字段定义 / 接口描述）→ 生成 data.js 的模拟数据结构。</action>

<action>读 `project-context.md`，确认原型产物输出路径。</action>

</step>

<step n="2" goal="设计原型结构">

<action>从 EXPERIENCE.md 的信息架构和 SPEC.md 的 Capabilities，列出「页面清单」：每个页面叫什么、URL path、从哪进、可点什么。</action>

<action>为每个页面定义「模拟数据结构」：基于 PRD 的字段定义，产出 data.js 里的 mock 数据。</action>

<action>列出「核心交互路径」：从 EXPERIENCE.md 的用户旅程提取 2-3 条最关键的端到端路径（如：登录 → 进入主页 → 创建一条记录 → 查看列表）。</action>

</step>

<step n="3" goal="产出 HTML 原型">

<action>写 `styles.css`：从 DESIGN.md 提取视觉变量（颜色、字体、圆角、间距），定义基础组件样式（按钮、输入框、卡片、导航栏）。</action>

<action>写 `index.html` + `app.js`：实现页面路由（hash 路由或简单 show/hide）、每个页面的 HTML 结构、核心交互的 JS 逻辑。</action>

<action>写 `data.js`：基于 PRD 字段定义的 mock 数据，按页面模块组织。</action>

<action>每个页面按需拆 `pages/page-{name}.js`，保持 `app.js` 不超过 300 行。</action>

</step>

<step n="4" goal="验证">

<action>自查：在浏览器打开 `index.html`，走通 2-3 条核心交互路径，确认能点、能跳、数据能展示。</action>

<action>检查清单：离线可运行 ✅ / 全页面可导航 ✅ / 核心交互可点跑 ✅ / 视觉对齐 DESIGN.md ✅ / 不调真实 API ✅</action>

</step>

<step n="5" goal="交付">

<action>输出原型目录到约定路径，告知用户原型位置和打开方式（双击 index.html）。</action>

<action>**写入进度**：更新 `project-progress.yaml`，将 `prototype` 阶段标记为 `done` + `completed_at`，`current_stage` 更新为 `client_gate`。若文件不存在，从 `templates/project-progress模板.yaml` 创建。</action>

<action>建议：原型完成后走 `delivery-client-gate` 的 A 入口（全新确认），附上原型目录给客户走查。</action>

</step>

</workflow>

## 给 LLM 的编码约束

- 用原生 HTML/CSS/JS（不依赖 React/Vue 等框架），保证离线可运行
- CSS 变量从 DESIGN.md 提取，命名规范：`--color-{name}` / `--font-{name}` / `--radius-{name}` / `--spacing-{name}`
- `data.js` 用固定 mock 数据，不调 API、不 fetch
- 交互逻辑用事件监听（addEventListener），不用框架的事件系统
- 每个页面不超过 200 行 HTML + 100 行 JS；超了就拆子模块
- 注释用中文，关键交互点加简短说明
