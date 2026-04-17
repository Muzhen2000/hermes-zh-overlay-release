# 安装与更新

## 前提

- 你已经按官方方式安装过 Hermes
- 本地 Hermes 源码目录是 `~/.hermes/hermes-agent`
- 个人配置、记忆、会话仍保存在 `~/.hermes` 下

## 一行应用最新中文包

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 -
```

## 一行应用指定版本

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --release 31e72764
```

## 这条命令具体会做什么

1. 更新 `~/.hermes/hermes-zh-overlay-release`
2. 读取当前 release 的 `manifest.json`
3. 将 `~/.hermes/hermes-agent` 强制对齐到该官方 commit
4. 清理旧版中文自动维护残留
5. 写入 `~/.hermes/localization/*.yaml`
6. 应用 `releases/<release>/patches/hermes-zh.patch`

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
- 不建议在应用中文包后再直接运行 `hermes update`；应等待这里发布对应版本再更新
