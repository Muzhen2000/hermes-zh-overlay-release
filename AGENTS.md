# AGENTS

这个文件是本仓库的远端 LLM 入口，也是后续维护者的唯一可执行规范之一。

它的目标不是“帮你把事情做快”，而是防止 Hermes 中文包维护变成补丁叠补丁、越修越散的维护灾难。

## 0. 先读完再动手

如果你是 LLM Agent，而用户让你处理这个仓库里的任何事，先完成下面 4 步，再考虑是否修改任何文件：

1. 先完整读本文件。
2. 如果本地存在 `~/.codex/skills/hermes-zh-release-guardrails/SKILL.md`，先显式使用它。
3. 先跑：
   `python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent`
4. 先把当前任务分到下面的第一类、第二类、第三类，再决定是否行动。

没有完成这 4 步之前，不要进入实现，不要改源码，不要说“已经完成”。

## 1. 这个仓库到底是什么

记住三句话：

1. 这个仓库的唯一目标，是为某一个指定官方 Hermes commit 提供一份按版本发货的最小中文包。
2. 这里追求的是“三者同版对应”，不是“永远追官方最新”。
3. 这里不是 Hermes 分叉版，不是长期自动维护系统，不是 Web UI 汉化仓库。

这里的“三者”指：

- 本地 Hermes 基线 commit
- 本地中文包 release
- 远端中文包仓库当前 release

正确状态是：

- 三者绑定到同一个官方 Hermes 版本
- 三者彼此一致
- 这可以不是官方当前最新，只要它们严格对应同一版即可

错误理解是：

- 只要官方又更新了，就必须马上追到最新
- 本地 Hermes 和中文包不是同一版也没关系
- 远端 release 与本地实际状态可以暂时错位

## 2. 这个仓库负责什么

仓库只负责两类内容：

- 终端中用户可见、非 LLM 生成的固定文案
- Telegram 中用户可见、非 LLM 生成的固定文案

这包括但不限于：

- 启动页固定说明文字
- 终端欢迎语
- 各皮肤的固定欢迎语、帮助头、固定思考状态提示语
- slash 命令注释
- slash 命令触发后的固定提示语，包括成功、失败、空状态、用法提示、加载中提示、确认/拒绝提示
- 固定二级选项提示语
- 用户发出消息后、LLM 回复前的固定状态提示语，包括 agent 初始化提示、busy 状态、spinner face + verb 组合、工具/记忆检索短状态行
- Telegram 中对应的固定命令说明与固定提示语

明确不包括：

- Web UI
- LLM 回答正文
- 发给模型的 system prompt、tool summary、内部控制文本
- 用户不可见的内部日志或运行时控制信息
- 与中文化无关的顺手修复、重构、格式化

注意：

- 不要只根据一个截图或一个皮肤做症状修补。
- 固定文案应按“同类问题”检查全部相关皮肤、终端面和 Telegram 面。
- 如果必须隐藏内部提示文本，只允许做展示层摘要，不得改真正送入模型的内容。

## 3. 六条阶梯原则

未来维护时，永远按这 6 条原则思考：

1. 非必要，不改源码。
2. 需要改源码时，只动最小化的用户可见面。
3. 最小化优先走外置数据，不要先改运行层。
4. 改核心文件时，默认只能做字符替换或最薄接线，不改控制流。
5. 只有极端必要时，才允许极小显示层适配。
6. 一切判断都以目标官方 commit 为基线，不在已经偏离的脏树上继续补丁。

这是硬约束，不是建议。

补充：

- 本仓库的本地强约束技能是 `~/.codex/skills/hermes-zh-release-guardrails/SKILL.md`。
- 如果接手线程环境可用该 skill，应先显式使用它，再继续本仓库维护。
- 就算没有 skill 可用，也必须把本文件当作远端仓库的等价 LLM 入口来执行，不能跳过。

## 4. 维护的默认工作流

### 4.1 先判断任务类型

先问自己：这是下面哪一种？

- 只是要确认三者是否一致
- 要做新的中文包 release
- 要做官方版本升级
- 要处理本地 Hermes 已经坏掉的紧急修复

不要默认用户一定要追官方最新。

### 4.2 如果只是确认一致性

做这几件事：

1. 读取 `release.json`
2. 读取当前 release 的 `manifest.json`
3. 检查本地 `~/.hermes/hermes-agent` 的 `HEAD`
4. 运行：
   `python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent`
5. 检查本地中文包仓库 `HEAD` 是否等于远端 `origin/main`

如果这些都成立，就不要为了“顺手升级”继续改动。

### 4.3 如果要做新的中文包 release

正确顺序只能是：

1. 确定目标官方 commit
2. 准备一棵干净的 Hermes 官方基线树
3. 比对旧官方 commit 与新官方 commit
4. 只检查终端和 Telegram 范围内的固定可见文案是否新增、变更或删除
5. 先复用旧 release 的词条与皮肤，再逐项核对是否仍然适用
6. 优先更新外置词条文件
7. 外置词条无法覆盖时，才做最小源码接线或字符替换
8. 重新生成新的 `hermes-zh.patch`
9. 生成新的 `releases/<new_release>/`
10. 运行校验和 smoke test
11. 全部通过后，才更新 `release.json` 的 `latest_release`

不要这样做：

- 不要先改中文包仓库，再倒推 Hermes
- 不要在旧 patch 或旧脏树上继续叠补丁
- 不要直接复制旧 patch 当成新 patch 而不重新生成

### 4.4 如果 Hermes 本地已经坏了

允许做最小的本地急救，但只为了恢复运行，不是为了把问题糊过去。

流程是：

1. 先做最小修复让 Hermes 起得来
2. 立刻验证运行确实恢复
3. 再从官方基线重新导出 patch
4. 再验证 patch 能在干净官方 worktree 上应用
5. 只有这样，才可以说问题解决

## 5. 允许什么，不允许什么

### 5.1 默认允许

- 终端启动页固定文案
- 终端欢迎语、帮助头、固定思考状态提示语
- 各皮肤固定文案
- terminal slash command descriptions
- terminal slash command fixed replies
- Telegram slash command descriptions
- Telegram slash command fixed replies
- empty-state / usage / success / failure 固定消息
- 用户发消息后到 LLM 回复前的固定状态行
- release patch / manifest / validation scripts / release-localization YAML

### 5.2 默认不允许

- Web UI changes
- model answer rewriting
- system prompt rewriting for translation purposes
- runtime translation bridges in `~/.hermes/localization/*.py`
- unrelated refactors
- “while I am here” cleanup outside localization scope

### 5.3 源码改动的允许形态

只有在外置词条不够时，才允许改源码。

允许的改动形态：

- 给现有用户可见固定文案接入一个最薄的 `_ui()` 风格取词条钩子
- 在现有字符串位置做字符替换
- 极小的皮肤文案读取接线
- 极小显示层适配

不允许的改动形态：

- 改命令分发逻辑
- 改会话状态流
- 改 Telegram callback 协议或内部 token
- 改模型交互文本
- 为了“统一优雅”而抽大层、搬大模块、重构结构
- 在一个问题上只修一个皮肤、一个提示语、一个截图症状，而不检查同类范围

## 6. 审计标准

每次维护完成后，必须重新做一轮“基线审计”。

审计时，逐个对照官方 commit 判断：

1. 这个文件为什么与官版不同？
2. 这处不同是否属于终端 / Telegram 固定可见中文化？
3. 这处不同能不能外置到数据层？
4. 如果不能外置，是否已经是最薄钩子？
5. 是否改变了控制流、运行路径、状态机或模型交互？
6. 这条改动是否是“整类问题”的解决，而不是某个表面症状的补丁？

如果答不清楚，就说明改动还不够收口。

### 6.1 源码审计三分类

以后做“源码收口审计”时，不要只看文件数。先把每个生产源码改动归类，再决定是否继续缩。

#### 第一类：稳定骨架

这是当前中文包的最小骨架。除非能用更外置、更薄的方式真实替换，否则默认冻结，不要为了追求更少文件数而反复折腾。

当前 release 的稳定骨架包括：

- `hermes_cli/skin_engine.py`
- `hermes_cli/commands.py`
- `hermes_cli/tips.py`
- `cli.py`
- `gateway/run.py`
- `gateway/platforms/telegram.py`
- `hermes_cli/banner.py`
- `agent/display.py`
- `agent/manual_compression_feedback.py`

对第一类文件的处理规则：

- 默认保留
- 不做“为减少文件数而减少文件数”的回退
- 只接受最薄的用户可见层接线
- 任何显示层例外都必须在 `manifest.json` 里显式登记

#### 第二类：叶子 UI 文件

这些文件属于用户可见面，但不是中文包的架构骨架。它们可以审计是否值得保留，但不能为了文件数去强行重构。

当前 release 的第二类文件包括：

- `hermes_cli/auth.py`
- `hermes_cli/status.py`
- `hermes_cli/debug.py`
- `hermes_cli/gateway.py`
- `hermes_cli/main.py`

对第二类文件的处理规则：

- 先问：去掉这里的中文，是否会明显破坏“默认中文”体验？
- 如果不会明显破坏，它才是优先回退候选
- 如果会明显破坏，就继续保留，不要为少几个文件而牺牲体验
- 不要为了收口第二类文件而引入新的结构重构

#### 第三类：规则失配

第三类不是某个用户可见文案，而是“规则层”和“真实代码层”不一致。

典型表现：

- `manifest.json` 里登记的显示层例外少于真实代码中的例外
- `AGENTS.md` / skill / manifest 描述的范围比真实改动面更小
- 规则说只读数据优先，但实际实现依赖了未声明的运行时桥

对第三类问题的处理规则：

- 优先级最高，先修它
- 先修文档/manifest/skill 与真实实现的错位，再谈“源码已经干净”
- 没有解决第三类问题，不准说系统已经收口

审计顺序固定为：

1. 先判断是不是第三类
2. 不是第三类，再判断是不是第二类
3. 剩下的通常就是第一类，视为稳定骨架

## 7. 版本规则

### 7.1 版本永远从官方基线来

不要把“已经改过的本地树”当成未来版本的基线。

每个 release 都必须满足：

- 对应一个明确的官方 Hermes commit
- patch 从那个官方 commit 重新生成
- 不在旧 release 上假设兼容
- 不把历史 patch 直接当新 patch 复制

### 7.2 三者一致的含义

三者一致，指的是：

- 本地 Hermes 基线 commit
- 本地中文包 release
- 远端中文包仓库当前 release

三者必须绑定到同一个官方 Hermes 版本。

如果三者不同版，就不算达标。

### 7.3 官方更新后的判断

如果官方更新没有触及本仓库范围，仍然可以发布新 release 绑定新的官方 commit，但原则是：

- patch 仍然必须基于新的官方 commit 重新生成
- 不允许直接在旧 release 上“假设兼容”
- 不允许为了凑新 release 而顺手扩大改动面

## 8. manifest 与 release 产物规则

`manifest.json` 不是摆设，必须真实反映当前 release：

- `allowed_source_files` 只列当前 release 真正允许改动的源码文件
- `localization_files` 只列当前 release 真正需要的词条文件
- `justified_non_text_logic` 只列真正必要的显示层例外

如果某个历史 release 的 manifest 里还有旧实现痕迹：

- 不要把它当成未来 release 的模板直接复制
- 先判断它是不是历史遗留
- 能收口就收口
- 不能立即收口，也要在文档里明确标注为历史遗留，而不是默认标准

## 9. 验证门槛

发新 release 前，至少确认这些事情：

- `scripts/verify_release.py` 通过
- patch 能基于目标官方 commit 干净应用
- `manifest.json` 的 `allowed_source_files` 与真实源码 diff 一致
- 允许列表之外的源码 diff 为 0
- `manifest.json` 的 `localization_files` 只列真正需要的文件
- `manifest.json` 的 `localization_files` 不包含 `.py` 运行时桥
- `ui.zh-CN.yaml` 覆盖 patch 中所有 `_cli_ui(...)` 与 `_gateway_ui(...)` 固定文案 key
- 历史遗留文件没有被错误当成未来标准继续带入
- Web UI 没有被纳入本仓库处理范围

推荐补充验证：

- 终端启动页能正常显示
- 可用技能数量正常，不出现异常归零
- `/help`、slash 命令注释、命令触发后的固定提示语仍正常
- 各皮肤固定欢迎语、帮助头、固定思考状态提示语仍正常；不能只测当前皮肤
- Telegram 固定命令说明与固定提示语仍正常

推荐测试集：

- `tests/tools/test_skills_tool.py`
- `tests/agent/test_display.py`
- `tests/hermes_cli/test_skin_engine.py`
- `tests/hermes_cli/test_banner.py`
- `tests/hermes_cli/test_commands.py`
- `tests/hermes_cli/test_tips.py`
- `tests/cli/test_cli_loading_indicator.py`
- `tests/cli/test_cli_localized_feedback.py`

如果某些测试因本机缺少可选依赖而无法运行，必须明确记录：

- 哪个测试没跑
- 没跑的具体原因
- 这不是“已通过”，只能算“环境受限未验证”

三者对齐时，至少还要额外确认：

- 本地 Hermes `HEAD` 等于当前 release 的 `official_commit`
- 本地中文包仓库 `release.json` 指向的 release 与当前 release 一致
- 本地中文包仓库 `HEAD` 与远端 `origin/main` 一致
- `verify_release.py --source-dir ~/.hermes/hermes-agent` 通过

只要这 4 条中任意一条不成立，就不能说“三者一致”。

## 10. 常见错误做法

以下做法过去都证明会把事情搞复杂，未来不要再犯：

1. 在已经汉化过的脏树上继续修补，而不是回到官方基线重做。
2. 用户指出一个问题，就只修那一个截图、那一个皮肤、那一句提示，而不检查同类范围。
3. 把本地化做成可执行运行时桥，而不是只读数据。
4. 为了修一个文案问题，顺手扩大到结构重构。
5. 保留已经不再对应真实代码路径的旧测试或旧说明。
6. 不做验证就宣称“全部完成”。

## 11. 新线程的默认工作流

如果你是一个没有上下文的新线程 LLM Agent，而用户让你“更新 Hermes”或“检查 Hermes 与中文包是否一致”，默认按下面的顺序执行。

先判断用户要的是哪一种：

### 场景 A：只要求三者一致

目标：

- 本地 Hermes
- 本地中文包
- 远端中文包仓库

三者都绑定在同一版 Hermes 上，并且彼此一致。

这时先做：

1. 读取 `release.json`
2. 读取当前 release 的 `manifest.json`
3. 检查本地 `~/.hermes/hermes-agent` 的 `HEAD`
4. 运行：
   `python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent`
5. 检查本地中文包仓库 `HEAD` 是否等于远端 `origin/main`

如果这几项都成立，就不要为了追官方最新而继续改动。

### 场景 B：要求升级到新的官方版本

只有当用户明确要求“升级到官方新版本”时，才进入升级流程。

这时再做：

1. 确认官方目标 commit
2. 从该官方 commit 的干净基线开始
3. 判断终端 / Telegram 固定可见文案是否进入新的汉化范围
4. 先复用旧 release 的词条与皮肤
5. 外置优先，源码最小
6. 重新生成 patch / manifest / release
7. 验证通过后再推送远端

## 12. 提交前最后自检

提交前问自己这 8 个问题：

1. 我是不是从官方基线开始，而不是从旧脏树开始？
2. 我是不是只处理了终端和 Telegram，而没有碰 Web UI？
3. 我是不是优先用了外置词条，而不是先改源码？
4. 我对源码的改动是不是只限于最小可见面？
5. 我有没有把问题按“同类固定文案”检查，而不是只修一个症状？
6. 我有没有避免再引入可执行本地化运行时桥？
7. 我的验证是不是已经真的跑过，而不是口头假设？
8. 这个 release 是否真的还能让用户得到“官方 Hermes + 对应最小中文包”？

如果其中任一项不能明确回答“是”，不要提交。
