# Hermes 中文最小包

这个仓库不分叉 Hermes，也不自动追官方最新。

它只做一件事：给**指定官方 Hermes commit**提供一份**最小中文包**，范围仅限：

- 终端中用户可见、非 LLM 生成的固定文案
- Telegram 中用户可见、非 LLM 生成的固定文案

它**不处理 Web UI**。Web UI 完全跟随官方源码。

## 使用方式

前提：你已经按官方方式安装过 Hermes，本地有 `~/.hermes/hermes-agent`。

应用当前最新中文包：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 -
```

应用指定版本：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --release 31e72764
```

校验当前本地状态：

```bash
python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
```

## 用户体验

你以后不需要关心“自动维护系统”。

流程只有两个：

1. 官方 Hermes 出新版本后，这个仓库发布一个对应版本的中文包。
2. 你或家人执行上面的同一条命令，把本地 Hermes 源码对齐到该官方版本，再应用该版本的最小中文包。

这条命令会：

- 更新本地这个中文包仓库
- 将 `~/.hermes/hermes-agent` 对齐到指定官方 commit
- 删除旧版中文自动维护残留
- 复制当前 release 的词条文件
- 应用当前 release 的最小 patch

它不会做这些事：

- 不处理 Web UI
- 不做无人值守自动追官方
- 不保留旧的自动维护系统
- 不修改 `~/.hermes` 下的个人配置、记忆、会话数据

## Release 结构

每个 release 目录都绑定一个官方 commit，例如：

```text
releases/31e72764/
  manifest.json
  patches/hermes-zh.patch
  localization/
    commands.zh-CN.yaml
    hermes_zh_runtime.py
    skills.zh-CN.yaml
    skins.zh-CN.yaml
    tips.zh-CN.yaml
    ui.zh-CN.yaml
```

## 维护原则

- 基线永远是官方 Hermes 指定 commit
- 非必要，不改源码
- 必须改源码时，只做最小可见面改动
- 不改控制流，不改条件块，不改运行路径
- Web UI 不处理
- 每个 release 都从官方基线重新生成最小 patch

详细安装说明见 [`docs/install.md`](./docs/install.md)。
