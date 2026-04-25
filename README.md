# Hermes 中文最小包

这是一个按版本发货的 Hermes 中文 overlay release 仓库，不是 Hermes 分叉版。

它的目标只有一个：

- 为某一个指定的官方 Hermes commit 提供一份最小、可复现、可验证的中文包

当前 release：

- 官方 Hermes commit：`023b1bff11c2a01a435f1956a0e2ac1773a065f3`
- 中文包 release：`023b1bff-discord1`

范围说明：

- 终端、Discord 中用户可见、非 LLM 生成的固定文案
- 当前版优先保持官方 Hermes 源码零 patch；只有官方已有的数据入口会实际生效
- 不处理 Web UI

当前这版覆盖的主要内容：

- 终端启动页固定文字
- 终端欢迎语
- slash 命令注释与固定回复
- 固定二级选项提示语
- LLM 回复前的固定状态提示语
- Discord 数据层说明词条
- release apply 对审计 baseline 的保留
- 当前版不包含 Hermes 源码 patch，因此终端命令固定回复和 Discord 固定回复仍跟随官方英文；后续若要完整中文化，必须单独批准极小显示层 hook

## 使用

1. 应用这一版中文包

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --release 023b1bff-discord1
```

2. 校验本机 Hermes 与这版中文包是否一致

```bash
python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
```

第二行通过，表示你本机的：

- Hermes 源码版本
- 本地中文包
- 当前 release

三者已经对应到同一版。

如果你只想跟随仓库当前最新 release，也可以直接执行：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 -
```

如果安装命令报：

- `curl: (6) Could not resolve host: raw.githubusercontent.com`

这说明是本机网络或 DNS 解析问题，不是中文包本身失败。先重试，或切换网络后再执行同一条命令。

## LLM Agent 入口

后续更新、继续汉化、校验一致性，先看：

- [AGENTS.md](./AGENTS.md)

给未来 LLM Agent 的工作约束、6 条原则、更新顺序、验证标准，都写在这里。
