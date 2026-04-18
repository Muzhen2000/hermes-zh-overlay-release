# Hermes 中文最小包

把这个仓库理解成一件事就够了：

**它是官方 Hermes 的按版本发货的最小中文包。**

它不是：

- 不是 Hermes 分叉版
- 不是自动维护系统
- 不是会自己长期改你本地源码的常驻工具

你用的始终是**官方 Hermes**。这个仓库只是给某个官方版本补上一层**终端 + Telegram 的最小中文包**。

## 范围

这个仓库只处理：

- 终端中用户可见、非 LLM 生成的固定文案
- Telegram 中用户可见、非 LLM 生成的固定文案

这个仓库不处理：

- Web UI
- LLM 回答内容
- 个人配置、记忆、会话、登录态、API key

## 普通用户怎么用

你以后只需要记住这 4 步：

1. 先按官方方式安装 Hermes。
2. 再执行一条命令应用中文包。
3. 然后正常使用 Hermes。
4. 等这个仓库发布新版本后，再执行同一条命令更新。

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

## 这条命令实际在做什么

它会：

- 更新本地 `~/.hermes/hermes-zh-overlay-release`
- 读取对应 release 的 `manifest.json`
- 将 `~/.hermes/hermes-agent` 对齐到该官方 commit
- 清理旧版中文自动维护残留
- 写入当前 release 的词条文件
- 应用当前 release 的最小 patch

它不会：

- 不处理 Web UI
- 不自动追官方最新
- 不常驻后台自动维护
- 不修改 `~/.hermes` 下的个人数据

## 你的使用心智

不要把它理解成“我的 Hermes 会自动更新、自动翻译、自动修补”。

正确理解是：

- 你始终在用官方 Hermes
- 这个仓库发布“某个官方版本对应的一份最小中文包”
- 你需要升级时，就把本地 Hermes 对齐到那个版本，再应用那一版中文包

所以它更像：

**官方 Hermes + 一个按版本发货的最小中文补丁包**

而不是一套长期在本地自行运转的维护系统。

## 给家人或另一台 Mac 怎么用

流程和你自己完全一样：

1. 先按官方方式安装 Hermes
2. 再运行上面的同一条命令
3. 如果你们都应用同一个 release，就会得到同一套 Hermes 源码版本和同一套中文包

不同机器之间不会共享这些个人内容：

- 会话
- 记忆
- 配置
- 登录态
- API key

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

## 维护说明

给未来维护这个仓库的人类或 LLM Agent：

- 用户安装与更新说明见 [docs/install.md](./docs/install.md)
- 仓库维护与继续汉化规则见 [AGENTS.md](./AGENTS.md)
