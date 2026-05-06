# Hermes 中文最小包

这是按版本发货的 Hermes 中文 overlay release 仓库，不是 Hermes 分叉版。

目标只有一个：为某一个指定官方 Hermes commit 提供一份最小、可复现、可验证的中文包。

## 当前版本

- 官方 Hermes commit：`946ef0ea1`
- 中文包 release：`946ef0ea1-terminal-discord1`
- 状态：**活跃维护中**

## 汉化范围

**仅汉化 Discord 和终端(TUI)的斜杠命令相关内容：**

- Discord 斜杠命令名称、描述、固定回复
- 终端(TUI)斜杠命令名称、描述、固定回复

**不汉化：**
- 皮肤/主题
- 其他平台（飞书、Telegram等）
- 工具说明
- 提示文案

## 应用命令

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$HOME/.hermes"
```

锁定版本：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$HOME/.hermes" --release 946ef0ea1-terminal-discord1
```

## 校验

```bash
python3 "$HOME/.hermes/hermes-zh-overlay-release/scripts/verify_release.py" --source-dir "$HOME/.hermes/hermes-agent"
```

## LLM Agent 入口

- [AGENTS.md](./AGENTS.md)
