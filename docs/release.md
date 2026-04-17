# 发布说明

当前发布真源由 [`release.json`](../release.json) 和 [`payload/localization/support-policy.json`](../payload/localization/support-policy.json) 共同定义，并会在验证通过后自动晋升。

## 当前发布状态

- `release_version`: `0.1.0`
- 官方仓库：`https://github.com/NousResearch/hermes-agent.git`
- 受支持 commit：以 `release.json` 和 `support-policy.json` 的当前值为准
- 失败包镜像：`~/Desktop/Hermes-ZH-Failures/latest`

## 发布流程

1. 先在隔离环境验证新的 Hermes 官方 commit。
2. 运行 `unattended-release` workflow。
3. workflow 会检测上游、构建候选并验证通过。
4. 如果通过，workflow 自动更新 `release.json` 和 `payload/localization/support-policy.json`，并推回 `main`。
5. 如果失败，workflow 先生成 failure bundle，再允许 `codex exec` 做最小修复。

## 失败时会发生什么

- 先生成 failure bundle
- 再把 failure bundle 上传为 artifact
- 同步一份到桌面路径
- 允许 `codex exec` 在候选 checkout 中做最小修复

## 维护边界

- 不把 Web UI 纳入这套 release 汉化系统
- 不直接追官方最新 `main`
- 不在失败时覆盖用户个人配置、记忆或会话数据
