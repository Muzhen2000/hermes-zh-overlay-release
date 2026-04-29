# 安装与更新

## 前提

- 你已经按官方方式安装过 Hermes。
- 本地 Hermes 源码目录是 `~/.hermes/hermes-agent`。
- 个人配置、记忆、会话、API key、登录态仍保存在 `~/.hermes` 下。

这个仓库提供的是：官方 Hermes 某个 commit + 对应该 commit 的最小中文包。它不是 fork，也不是自动追最新的长期补丁系统。

## 应用最新中文包（推荐）

生产环境推荐显式写出 `--hermes-home "$HOME/.hermes"`，这样可以确认中文包应用到默认 Hermes home，不依赖脚本默认值。

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$HOME/.hermes"
```

## 校验一致性

```bash
python3 "$HOME/.hermes/hermes-zh-overlay-release/scripts/verify_release.py" --source-dir "$HOME/.hermes/hermes-agent"
```

这两行是测试用户的标准路径：第一行应用，第二行验证。

## 应用指定版本

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$HOME/.hermes" --release 58a6171b-terminal-discord1
```

## 安全测试远端命令

如果只想确认远端命令有效，但不想修改自己的 `~/.hermes`，使用临时 Hermes home：

```bash
tmp="$(mktemp -d /tmp/hermes-zh-apply.XXXXXX)"
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$tmp"
python3 "$tmp/hermes-zh-overlay-release/scripts/verify_release.py" --repo-root "$tmp/hermes-zh-overlay-release" --source-dir "$tmp/hermes-agent"
```

## 这条命令会做什么

1. 更新 `~/.hermes/hermes-zh-overlay-release`。
2. 读取 `release.json` 和当前 release 的 `manifest.json`。
3. 将 `~/.hermes/hermes-agent` 对齐到 manifest 绑定的官方 commit。
4. 写入 `~/.hermes/localization/*.yaml`。
5. 同步 release 附带的 `~/.hermes/skins/*.yaml`。
6. 如果 manifest 声明 patch，则应用 `releases/<release>/patches/hermes-zh.patch`。
7. 清掉默认 profile 与 named profiles 下旧的 `.update_check`，避免升级后仍误报“落后若干提交”。

## 不会动的内容

- `~/.hermes/sessions`
- `~/.hermes/memory*`
- `~/.hermes/config.yaml`
- API key、登录态、个人数据
- Web UI
- Telegram / 飞书网关运行面

## 当前 release 的预期效果

- 终端和 Discord 中属于本仓库范围的固定文案变为中文。
- Discord slash 命令说明包括显式注册命令和动态注册命令。
- Web UI 保持官方原样。
- 模型路由、provider 参数、Discord command value/custom_id 等协议字段保持官方语义。

## 常见问题

- 如果安装命令报 `curl: (6) Could not resolve host: raw.githubusercontent.com`，这是本机网络或 DNS 解析问题，不是中文包本身失败。
- 不建议应用中文包后直接运行 `hermes update`。如果手动更新 Hermes 到官方新版本，应等待这里发布对应 release 后再应用中文包。
