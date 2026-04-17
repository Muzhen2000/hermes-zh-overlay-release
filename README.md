# Hermes 中文化无人值守发布

这是 Hermes 中文化 overlay 的公开 release 仓库，不是 Hermes 本体的 fork，也不是用户端安装器。

它负责三件事：

- 记录当前受支持的 Hermes 官方 commit
- 维护中文化 payload、失败包和无人值守工作流
- 在 GitHub Actions 上验证候选版本，并在失败时输出可接手的失败包

## 当前状态

- 官方基线：见 [`release.json`](./release.json)
- 支持策略：见 [`payload/localization/support-policy.json`](./payload/localization/support-policy.json)
- 无人值守工作流：见 [`.github/workflows/unattended-release.yml`](./.github/workflows/unattended-release.yml)

## 仓库内容

- `scripts/`：上游检测、候选构建、失败包收集、Codex remediation 调度
- `payload/`：发布给本地 Hermes 维护器消费的策略和脚本
- `codex/`：失败时交给 `codex exec` 的提示和输出 schema
- `tests/`：release 流水线、失败包和 remediation 契约测试
- `docs/`：安装、发布和失败包说明

## 如何使用

如果你是维护者：

1. 修改 `release.json` 和 `payload/localization/support-policy.json`
2. 本地运行 `python3 -m pytest tests -q`
3. 推送 `main`
4. 在 GitHub 上手动或定时触发 `unattended-release`

如果你是想了解本仓库如何落地：

- 安装与本地检查：见 [`docs/install.md`](./docs/install.md)
- 发布流程：见 [`docs/release.md`](./docs/release.md)
- 失败包格式：见 [`docs/failure-package.md`](./docs/failure-package.md)

## 设计边界

- 不维护 Web UI 的汉化，Web UI 使用 Hermes 官方自带的中/英切换
- 不直接追官方 `main`，只追 `release.json` / `support-policy.json` 声明的受支持版本
- 失败时先收集失败包，再允许 remediation

