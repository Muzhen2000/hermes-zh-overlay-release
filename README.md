# Hermes 中文最小包

这是**官方 Hermes `31e72764`** 对应的**最小中文包**。

- 汉化范围：终端、Telegram 中用户可见且非 LLM 生成的固定文案

当前版本：

- 官方 Hermes：`31e72764`
- 中文包 release：`31e72764`

具体汉化内容：

- 终端启动页固定文字
- 终端欢迎语
- slash 命令注释
- slash 命令触发后的固定提示语
- 固定二级选项提示语
- LLM 回复前的固定状态提示语
- Telegram 中对应的固定命令说明与固定提示语

## 使用

1. 应用这一版中文包

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --release 31e72764
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

## LLM Agent 入口

后续更新、继续汉化、校验一致性，先看：

- [AGENTS.md](./AGENTS.md)

给未来 LLM Agent 的工作约束、6 条原则、更新顺序、验证标准，都写在这里。
