# Hermes 中文化无人值守发布

公开 release 仓库，负责 Hermes 中文化 overlay 的发布、验证和失败接手。

## 状态

- 官方基线：[`release.json`](./release.json)
- 支持策略：[`payload/localization/support-policy.json`](./payload/localization/support-policy.json)
- 无人值守工作流：[`.github/workflows/unattended-release.yml`](./.github/workflows/unattended-release.yml)

## 入口

- 安装与本地检查：[`docs/install.md`](./docs/install.md)
- 发布流程：[`docs/release.md`](./docs/release.md)
- 失败包格式：[`docs/failure-package.md`](./docs/failure-package.md)
- 变更记录：[`CHANGELOG.md`](./CHANGELOG.md)

## 仓库内容

- `scripts/`：上游检测、候选构建、失败包收集、Codex remediation 调度
- `payload/`：发布给本地 Hermes 维护器消费的策略和脚本
- `codex/`：失败时交给 `codex exec` 的提示和输出 schema
- `tests/`：release 流水线、失败包和 remediation 契约测试
- `docs/`：安装、发布和失败包说明

## 约束

- 不维护 Web UI 的汉化，Web UI 使用 Hermes 官方自带的中/英切换
- 不直接追官方 `main`，只追 `release.json` / `support-policy.json` 声明的受支持版本
- 失败时先收集失败包，再允许 remediation
