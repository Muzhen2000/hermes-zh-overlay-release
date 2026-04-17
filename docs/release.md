# 发布说明

当前发布真源由 [`release.json`](../release.json) 和 [`payload/localization/support-policy.json`](../payload/localization/support-policy.json) 共同定义。

## 当前发布状态

- `release_version`: `0.1.0`
- 官方仓库：`https://github.com/NousResearch/hermes-agent.git`
- 受支持 commit：`5b4773fc20e844e784d1b710adaa0cfcc5e14d87`
- 失败包镜像：`~/Desktop/Hermes-ZH-Failures/latest`

## 发布流程

1. 先在隔离环境验证新的 Hermes 官方 commit。
2. 更新 `release.json` 和 `payload/localization/support-policy.json`。
3. 本地跑 `python3 -m pytest tests -q`。
4. 推送 `main` 到 GitHub。
5. 手动或定时触发 `unattended-release` workflow。
6. 通过后再把新版本标为受支持版本。

## 失败时会发生什么

- 先生成 failure bundle
- 再把 failure bundle 上传为 artifact
- 同步一份到桌面路径
- 允许 `codex exec` 在候选 checkout 中做最小修复

## 维护边界

- 不把 Web UI 纳入这套 release 汉化系统
- 不直接追官方最新 `main`
- 不在失败时覆盖用户个人配置、记忆或会话数据

