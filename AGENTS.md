# AGENTS

这个文件给未来接手此仓库的人类维护者或 LLM Agent 看。

目标只有一个：

**为指定官方 Hermes commit 提供一份最小中文包。**

请先读完本文，再决定是否修改任何东西。

## 1. 先理解这个仓库是什么

这个仓库：

- 不分叉 Hermes
- 不维护长期自动更新系统
- 不做 Web UI 汉化
- 不修改用户的个人配置、记忆、会话、登录态

这个仓库只负责：

- 终端中用户可见、非 LLM 生成的固定文案
- Telegram 中用户可见、非 LLM 生成的固定文案

这包括但不限于：

- 启动页中的固定说明文字
- 终端欢迎语
- 各皮肤的固定欢迎语、帮助头、思考状态提示语
- slash 命令注释
- slash 命令触发后的固定提示语
- 固定的二级选项提示语
- 用户发出消息后、LLM 回复前的固定状态提示语
- Telegram 中对应的固定命令说明与固定提示语

这明确不包括：

- Web UI
- LLM 回答正文
- 发给模型的 system prompt / tool summary / 内部控制文本
- 与用户不可见的内部日志或运行时控制信息

## 2. 永远遵守的边界

必须遵守：

1. 基线永远是官方 Hermes 指定 commit。
2. 非必要，不改 Hermes 源码。
3. 必须改源码时，只做最小可见面改动。
4. 不改控制流，不改缩进结构，不改条件块，不改运行路径。
5. 不在已经本地汉化过的脏树上继续补丁。
6. 每个 release 都必须从目标官方 commit 重新生成最小 patch。

默认禁止：

- 新建自动维护系统
- 定时任务、LaunchAgent、cron、自愈链路
- 失败包上报链路
- 为了“顺手优化”而做源码重构
- 扩大到 Web UI
- 翻译 LLM 生成内容
- 改写发给模型的内部提示文本
- 以“便于汉化”为名扩大源码改动面

## 3. 仓库内关键文件

- `release.json`
  当前发布索引；`latest_release` 指向默认发布版本。
- `releases/<release>/manifest.json`
  该版本的元数据、允许修改的源码文件列表、词条文件列表。
- `releases/<release>/localization/*`
  外置词条与运行时辅助文件。
- `releases/<release>/skins/*`
  该版本要随 release 一起分发的自建皮肤 YAML。
- `releases/<release>/patches/hermes-zh.patch`
  该官方 commit 对应的最小源码 patch。
- `scripts/apply_release.py`
  用户安装/更新入口。
- `scripts/verify_release.py`
  版本一致性与本地状态校验入口。

## 4. 当官方 Hermes 更新时，正确顺序是什么

**先更新 Hermes 基线，再做新的中文包。不要反过来。**

正确顺序：

1. 确定目标官方 commit。
2. 将本地 Hermes 源码检出到该官方 commit，确保它是官方基线。
3. 对比旧官方 commit 与新官方 commit，找出是否有新的“终端 / Telegram 固定可见文案”进入可汉化范围。
4. 优先更新外置词条文件。
5. 若此版本需要分发自建皮肤，同步整理 `releases/<new_commit>/skins/*.yaml`。
6. 只有外置词条无法覆盖时，才做最小源码替换。
7. 从该官方 commit 重新生成新的 `hermes-zh.patch`。
8. 创建新的 `releases/<new_commit>/` 目录。
9. 运行校验与 smoke test。
10. 通过后，再更新 `release.json` 的 `latest_release`，并推送仓库。

不要这样做：

- 不要先改中文包仓库，再倒推 Hermes。
- 不要在旧的本地汉化结果上继续叠补丁。
- 不要直接复制旧 patch 当成新 patch 而不重新生成。

## 5. 继续汉化时，先检查什么

每次接手前，先检查 4 件事：

1. 当前 `release.json` 指向的 release 是哪个官方 commit。
2. 本地 `~/.hermes/hermes-agent` 是否已经回到目标官方 commit。
3. 旧 release 中哪些词条和皮肤可以直接复用。
4. 官方这次更新是否真的触及了终端 / Telegram 可见固定文案。

如果第 4 项答案是否定的，也不要顺手扩展汉化范围；只在有必要时更新 release 绑定的官方 commit。

## 6. 如何判断“这次官方更新需不需要继续汉化”

先看官方更新是否触及以下范围：

- CLI 启动页、提示语、状态输出
- slash 命令注释与成功/失败提示
- 终端中的固定 spinner / status / notice 文案
- Telegram slash 命令注释
- Telegram 中非 LLM 生成的固定提示语

如果官方更新没有触及这些范围，仍然可以发布一个新 release 来支持新的官方 commit，但原则是：

- patch 仍然必须基于新的官方 commit 重新生成
- 不允许直接在旧 release 上“假设兼容”
- 不允许为了凑新 release 而顺手扩大改动面

## 7. 汉化时的优先级

按这个顺序做：

1. 外置词条替换
2. 外置运行时辅助
3. 极小源码字符替换
4. 仅在绝对必要时做极小显示层适配

第 4 条的例外必须非常少。当前已知可接受的例子是：

- 为了中文宽字符显示正确，做极小的终端显示宽度适配

这种例外必须满足：

- 只影响显示层
- 不改变业务逻辑
- 在 `manifest.json` 中可解释

## 8. 推荐的续做方式

未来的人类或 LLM Agent 接手时，按这个顺序执行：

1. 先更新并对齐本地 Hermes 到目标官方 commit。
2. 查看旧 release 的词条与皮肤，优先复用已有成果。
3. 检查新 commit 中是否新增了终端 / Telegram 固定文案。
4. 能用外置词条解决的，不碰源码。
5. 外置词条不够时，才做最小源码接线或字符替换。
6. 重新生成 patch，并确保 patch 只覆盖 `manifest.json` 允许的文件。
7. 运行校验与 smoke test。
8. 只有全部通过后，才更新 `release.json` 并推送。

## 9. 生成新 release 的工作方式

建议流程：

1. 记录旧 release 的官方 commit 与新目标 commit。
2. 从官方新 commit 开始工作，不从当前汉化工作树开始。
3. 复用已有中文词条，但逐项检查是否仍然适用。
4. 只保留真正必要的源码改动。
5. 生成 `releases/<new_commit>/manifest.json`。
6. 生成 `releases/<new_commit>/localization/*`。
7. 若要随 release 分发自建皮肤，生成 `releases/<new_commit>/skins/*`。
8. 生成 `releases/<new_commit>/patches/hermes-zh.patch`。
9. 校验通过后，更新 `release.json`。

## 10. 家人一行命令体验的底线

发布仓库必须持续保证这一点：

- 家人只需要先按官方方式安装 Hermes
- 然后执行一条命令，就能得到对应版本的中文 Hermes
- 不需要你的源码仓库
- 不需要手工 patch
- 不需要自己判断先后顺序
- 不应覆盖她自己的配置、记忆、会话和登录态

如果某次维护会破坏这条体验，就说明方案偏离了本仓库的目标。

## 11. 验收标准

发新 release 前，至少确认这些事情：

- `scripts/verify_release.py` 通过
- 允许改动文件列表与 `manifest.json` 一致
- 允许列表之外的源码 diff 为 0
- patch 能基于目标官方 commit 干净应用
- `hermes status` 等基础终端命令 smoke 正常
- 终端与 Telegram 的新增固定文案已覆盖
- Web UI 没有被纳入本仓库处理范围

## 12. 提交前最后自检

问自己 5 个问题：

1. 我是不是从官方基线开始，而不是从旧脏树开始？
2. 我是不是只处理了终端和 Telegram，而没有碰 Web UI？
3. 我是不是优先用了外置词条，而不是直接改源码？
4. 我对源码的改动是不是只限于最小可见面？
5. 这个 release 是否真的可以让用户得到“官方 Hermes + 对应最小中文包”？

如果其中任一项不能明确回答“是”，不要提交。
