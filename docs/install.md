# 安装与更新

## 前提

- 你已经按官方方式安装过 Hermes
- 本地 Hermes 源码目录是 `~/.hermes/hermes-agent`
- 个人配置、记忆、会话仍保存在 `~/.hermes` 下

把这个仓库理解成：

- 官方 Hermes 某个版本
- 对应一份这个版本的最小中文包
- 如果 release 附带了自建皮肤，也会一并同步到 `~/.hermes/skins/`

## 一行应用最新中文包

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 -
```

## 一行应用指定版本

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --release a828daa7
```

## 给家人的最短说明

如果她已经按官方方式安装过 Hermes，她只需要执行这一条命令：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 -
```

她不需要：

- 你的 `~/.hermes/hermes-agent` 源码仓库
- 手工打 patch
- 自己判断要先更新哪个仓库

这条命令会自动完成：

- 拉取这个公开仓库的当前 release
- 把她本地 Hermes 对齐到该 release 绑定的官方 commit
- 应用这一版最小中文包
- 同步这一版附带的皮肤文件

她运行后，预期体验是：

- 终端与 Telegram 中属于本仓库范围的固定文案变为中文
- Web UI 保持官方原样
- 她自己的会话、记忆、配置和登录态不被覆盖

## 这条命令具体会做什么

1. 更新 `~/.hermes/hermes-zh-overlay-release`
2. 读取当前 release 的 `manifest.json`
3. 将 `~/.hermes/hermes-agent` 强制对齐到该官方 commit
4. 清理旧版自动维护残留（仅为迁移收尾，不属于当前系统）
5. 写入 `~/.hermes/localization/*.yaml`
6. 如果该 release 附带皮肤，则写入 `~/.hermes/skins/*.yaml`
7. 应用 `releases/<release>/patches/hermes-zh.patch`
8. 清掉默认 profile 与 named profiles 下旧的 `.update_check`，避免升级后仍误报“落后若干提交”

## 不会动的内容

- `~/.hermes/sessions`
- `~/.hermes/memory*`
- `~/.hermes/config.yaml`
- 你的 API key、登录态、个人数据

## 校验

```bash
python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
```

## 注意

- 这个仓库不处理 Web UI
- 发布了新 release 后，再运行同一条命令更新
- release 附带的同名皮肤文件会被同步更新，但不会删除你额外自建的其他皮肤
- 不建议在应用中文包后再直接运行 `hermes update`；应等待这里发布对应版本再更新
- 如果你手动更新过 Hermes 到官方新版本，但这里还没有发布对应 release，请先不要应用不匹配的中文包
