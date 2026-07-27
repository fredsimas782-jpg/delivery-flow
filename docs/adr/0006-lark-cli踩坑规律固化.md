# ADR 0006: lark-cli 踩坑规律固化到 SKILL 文档

- **日期**: 2026-07-24
- **状态**: 已采纳

## 背景

delivery-feishu-sync 是唯一带具体命令行操作的 skill。在首个消费方项目实跑时，lark-cli 暴露了若干非直观行为，如果不记录下来，下次使用者（包括自己）会重复踩坑。

## 决策

将实战踩坑规律整理为速查段，内嵌在 `delivery-feishu-sync/SKILL.md:70-86`，包括：

1. 子任务 `--data` 必须显式带 `tasklists:[{tasklist_guid}]`（schema 不标 required，实际隐性必填），否则 500
2. 优先级 custom field 不能设在子任务上；多个 custom_fields 同设会报 `permission_denied`（校验失败），简化到只设阶段状态
3. 代理探测的 `[lark-cli] [WARN]` 行污染 stdout，解析 JSON 前需 `grep -v` 过滤
4. `--data @file` 路径必须相对当前工作目录（给绝对路径报 "must be a relative path"）
5. 写操作 `--output` 不落盘，须直接解析 stdout；`--page-all` 与 `--output` 互斥；删除需加 `--yes`
6. 飞书 API 无法建"清单文件夹"（左侧分组），只能靠命名前缀归拢；子任务只有一层

## 后果

- 正面：踩坑知识不丢失，新使用者可直接避开已知陷阱
- 正面：减少因为 CLI 非直观行为导致的挫败感
- 代价：文档版本可能落后于 CLI 更新（需定期验证）

## 出处

- `delivery-feishu-sync/SKILL.md:70-86`
- 实跑项目：首个消费方 AI 应用 PoC 12 子任务
