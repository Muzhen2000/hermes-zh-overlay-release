# Changelog

## Unreleased

- 增加 macOS 一行安装器 `scripts/install_local_overlay.py`。
- 本地 `maintain` 失败时自动生成失败包并镜像到 `~/Desktop/Hermes-ZH-Failures/latest`。
- 安装文档补充普通用户视角、验收命令和安全的 `--no-bootstrap --no-maintain` 测试模式。
- 将公开仓库的 `payload/scripts/hermes_zh_overlay_manager.py` 同步为真实本地维护器实现，不再只是占位 helper。
- 补充 payload manager 回归测试，覆盖“空 patch 自愈”和“误更新后回到 supported_commit”两条关键恢复路径。
- 将 release truth 前移到当前已验证通过的官方提交 `01906e99dd225b7946c770479fcd9cc2949e7104`。

## 0.1.0

- 初始化 Hermes 中文化无人值守发布仓库。
- 建立 release 真源、支持策略、候选验证、failure bundle 和 Codex remediation 契约。
- 在本地测试和真实 GitHub Actions 中验证了正常路径与失败路径。
- 补充公开仓库说明、安装说明和发布说明。
