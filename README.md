# Hermes 中文化无人值守发布

公开 release 仓库，负责 Hermes 中文化 overlay 的发布、验证和失败接手。

## 适用对象

- 维护者：更新支持版本、修正 release 流程、发布新版本
- 失败接手者：根据 failure bundle 定位问题并做最小修复
- 普通用户：只需要跟随 release 仓库发布的结果，不直接改这里

## 用户体验视角

如果你是普通用户，可以把它理解成：

- 你平时直接把 Hermes 当成“默认中文的 Hermes”来用
- 你正常使用终端/TUI 和 Telegram，不需要自己去找哪些英文该翻
- 你想更新时，正常运行 `hermes update`
- 大多数更新不会碰到中文化范围，所以更新后通常不需要你做额外处理
- 更新后只要随手看一眼启动页、`/help` 和常用提示语是不是还在中文就够了

这套系统真正想给你的体验是：

- 平时只管用，不用管 release 仓库内部怎么工作
- Hermes 更新时，系统会先检查这次更新有没有碰到“需要中文化”的范围
- 没碰到就直接通过；碰到了才做最小修补
- 如果自动处理失败，本地应当停在旧的稳定版本，而不是把 Hermes 直接更新坏

一句话：

- 普通用户的正确心智不是“我在维护一个魔改 fork”
- 而是“我在用官方 Hermes，只是默认带了一层受控的中文 overlay”

## 状态

- 官方基线：[`release.json`](./release.json)
- 支持策略：[`payload/localization/support-policy.json`](./payload/localization/support-policy.json)
- 本地维护器实现：[`payload/scripts/hermes_zh_overlay_manager.py`](./payload/scripts/hermes_zh_overlay_manager.py)
- 无人值守工作流：[`.github/workflows/unattended-release.yml`](./.github/workflows/unattended-release.yml)
- 自动晋升：workflow 验证通过后会自动更新 `release.json` / `support-policy.json` 并推回 `main`

## 入口

- 安装与本地检查：[`docs/install.md`](./docs/install.md)
- 发布流程：[`docs/release.md`](./docs/release.md)
- 失败包格式：[`docs/failure-package.md`](./docs/failure-package.md)
- 变更记录：[`CHANGELOG.md`](./CHANGELOG.md)
- 贡献规范：[`CONTRIBUTING.md`](./CONTRIBUTING.md)
- 许可证：[`LICENSE`](./LICENSE)

## 仓库内容

- `scripts/`：上游检测、候选构建、失败包收集、Codex remediation 调度
- `payload/`：发布给本地 Hermes 维护器消费的策略和脚本，其中 `support-policy.json` 是支持真源，`hermes_zh_overlay_manager.py` 是本地自愈维护器
- `codex/`：失败时交给 `codex exec` 的提示和输出 schema
- `tests/`：release 流水线、失败包和 remediation 契约测试
- `docs/`：安装、发布和失败包说明

## 约束

- 不维护 Web UI 的汉化，Web UI 使用 Hermes 官方自带的中/英切换
- 不直接追官方 `main`，只追 `release.json` / `support-policy.json` 声明的受支持版本
- 失败时先收集失败包，再允许 remediation
