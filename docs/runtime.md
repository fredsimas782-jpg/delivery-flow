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
- `trace`：报告 SPEC → Story → 映射 → 评测/验收链路的缺项；
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

## 后续边界

真实飞书 API、写入适配器、增量同步、商务 CRM 和完整流程平台不属于当前运行时自动化范围。
