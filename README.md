# Hermes 中文最小包

这是按版本发货的 Hermes 中文 overlay release 仓库，不是 Hermes 分叉版。

目标只有一个：为某一个指定官方 Hermes commit 提供一份最小、可复现、可验证的中文包。

## 当前版本

- 官方 Hermes commit：`e5647d7863d306c8f479e1da011ebe4a4848d56d`
- 中文包 release：`e5647d78-terminal-discord1`
- 范围：终端 + Discord 中用户可见、非 LLM 生成的固定文案
- 不处理：Web UI、Telegram、飞书、模型路由、provider 协议、用户配置、登录态

当前 release 带有一份受控 Hermes 源码 patch。它只做显示层中文取词钩子和 CJK 终端显示适配，不改命令分发、会话状态机、模型请求或 Discord 协议字段。

## 覆盖内容

- 终端启动页、欢迎语、状态栏、等待提示、工具/记忆检索短状态行
- 终端 slash 命令说明、固定回复、空状态、用法提示、成功/失败消息
- 全部内置皮肤和本包附带皮肤的固定欢迎语、帮助头、spinner 词组
- Discord slash 命令说明、参数说明、固定回复、按钮标签、model picker、approval/update 卡片
- Discord 动态命令说明：由 Hermes 命令注册表生成的命令也会走中文说明

## 两行测试命令

1. 应用仓库当前最新中文包：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 -
```

2. 校验本机 Hermes 与中文包是否一致：

```bash
python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
```

第二行通过，表示本机 Hermes 源码、本地中文包、当前 release 已经对应到同一版。

如果要锁定当前 release：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --release e5647d78-terminal-discord1
```

如果安装命令报 `curl: (6) Could not resolve host: raw.githubusercontent.com`，这是本机网络或 DNS 解析问题，不是中文包本身失败。切换网络或稍后重试同一条命令。

## LLM Agent 入口

后续更新、审计、继续汉化、校验三者一致性，先看：

- [AGENTS.md](./AGENTS.md)
- [docs/audit-2026-04-25.md](./docs/audit-2026-04-25.md)

本仓库只保留当前可验证 release。历史 Kimi、飞书、Telegram、旧 gateway release 目录已删除，避免未来 agent 把旧补丁当成新基线。
