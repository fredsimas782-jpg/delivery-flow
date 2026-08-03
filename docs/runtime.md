# 运行时自动化边界

## 定位

`delivery-flow` 的运行时自动化只做本地确定性检查和预演，不建设完整流程平台。

```text
需求规格真源：本地 SPEC / PRD / Story
执行状态真源：飞书
本地 sprint-status.yaml：飞书单向拉取的只读镜像
本地 project-progress.yaml：流水线宏观阶段追踪（关卡 skill 自动写入）
```

## 命令

在仓库根目录运行：

```bash
python -m scripts.delivery_flow.cli check --root <项目根目录>
python -m scripts.delivery_flow.cli trace --root <项目根目录>
python -m scripts.delivery_flow.cli status --root <项目根目录>
python -m scripts.delivery_flow.cli dry-run --root <项目根目录>
python -m scripts.delivery_flow.cli progress --root <项目根目录>
```

增加 `--json` 输出机器可读 JSON。所有命令默认只读，不连接网络。

## 能力边界

- `check`：检查 SPEC、客户确认、技术就绪、Story、映射表和流程乱序；
- `trace`：报告 商机 → SPEC → Story → 映射 → 评测/验收链路的缺项（存在商机编号 Trace 根时向上游延伸到售前）；
- `status`：只读聚合本地状态镜像（Story 粒度）；
- `dry-run`：预览飞书任务操作，不实际调用飞书或写入映射表；
- `progress`：显示流水线宏观阶段（读 `project-progress.yaml`，无则回退到产物扫描推断）。

程序不能代替客户签字、技术判断、Tier2 专家标注或客户验收。`unknown` 不折算为通过。

## 退出码

| 代码 | 含义 |
|---:|---|
| 0 | 通过或只有 warning |
| 1 | 存在流程阻断项 |
| 2 | 输入缺失、格式错误或 schema 问题 |
| 3 | 发生禁止的网络或写操作 |
| 4 | 内部异常 |

## 售前/商务的纳入方式

售前编排（`delivery-presales`）、签约关卡（`delivery-deal-gate`）与 CRM 同步（`delivery-crm-sync`）已作为流水线上游一环纳入，与其它 `delivery-*` skill 同为纯插件流程。它们对运行时的唯一要求是：`core.py` 识别 `opportunity`/`proposal`/`deal_gate` 三个宏观阶段、`trace_project` 在存在商机编号（Trace 根）时向上游延伸。**运行时本身仍只读**——商机/客户/合同数据的实际写入由 `lark-base` skill 承担，`core.py` 不联网、不写飞书，与需求侧 `delivery-feishu-sync` 的分工一致。

## 后续边界

真实飞书 API、写入适配器、增量同步和完整流程平台不属于当前运行时自动化范围（CRM 数据写入同样交由 lark skill，运行时只读不变）。
