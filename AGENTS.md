# AGENTS

这个文件给未来接手此仓库的人类维护者或 LLM Agent 看。

先记住一句话：

**这个仓库的唯一目标，是为指定官方 Hermes commit 提供一份按版本发货的最小中文包。**

再记住一句话：

**这里追求的是“三者同版对应”，不是“永远追官方最新”。**

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

不要把它理解成：

- Hermes 分叉版
- 长期自动维护系统
- 会自己持续追官方最新并自愈的后台工具
- Web UI 汉化仓库

请先完整读完本文，再决定是否修改任何东西。

## 1. 用户侧目标

这个仓库必须持续保证的用户体验只有一个：

- 用户先按官方方式安装 Hermes
- 再执行本仓库提供的一条命令
- 得到“官方 Hermes + 对应版本的最小中文包”
- 不需要维护者自己的 Hermes 源码副本
- 不需要手工 patch
- 不需要自己判断先后顺序
- 不应覆盖用户自己的配置、记忆、会话、登录态、API key

如果某次维护会破坏这条体验，就说明方案偏离了本仓库的目标。

补充：

- 用户得到的应该始终是“**某一版**官方 Hermes + **这一版对应的**最小中文包”。
- 这个概念比“官方最新”更重要。
- 如果本地 Hermes、中文包 release、远端仓库 release 不是同一版，就不算达标。

## 2. 作用范围

这个仓库只负责：

- 终端中用户可见、非 LLM 生成的固定文案
- Telegram 中用户可见、非 LLM 生成的固定文案

这包括但不限于：

- 启动页固定说明文字
- 终端欢迎语
- 各皮肤的固定欢迎语、帮助头、固定思考状态提示语；必须覆盖全部内置皮肤和本仓库随包分发的自建皮肤，不能只修当前正在使用的皮肤
- slash 命令注释
- slash 命令触发后的固定提示语，包括成功、失败、空状态、用法提示、加载中提示、确认/拒绝提示
- 固定二级选项提示语
- 用户发出消息后、LLM 回复前的固定状态提示语，包括 agent 初始化提示、命令 busy 状态、spinner face + verb 组合、工具/记忆检索的短状态行
- Telegram 中对应的固定命令说明与固定提示语

这明确不包括：

- Web UI
- LLM 回答正文
- 发给模型的 system prompt、tool summary、内部控制文本
- 用户不可见的内部日志或运行时控制信息
- 与中文化无关的“顺手修复”或重构

注意：

- 不要只根据一个截图或一个皮肤做症状修补。
- 在范围内的固定文案，应按“同类问题”检查全部相关皮肤、终端面和 Telegram 面。
- 如果不得不隐藏内部提示文本，只允许做“展示层摘要”，不得改写真正发给模型的内容。例如 skill 调用可在终端里显示“正在加载技能：xxx”，但不能为了汉化而改掉实际送入模型的 skill invocation payload。

## 3. 六条阶梯原则

未来维护时，永远按这 6 条原则思考：

1. 非必要，不改源码。
2. 需要改源码时，只动最小化的用户可见面。
3. 最小化优先走外置数据，不要先改运行层。
4. 改核心文件时，默认只能做字符替换或最薄接线，不改控制流。
5. 只有极端必要时，才允许极小显示层适配。
6. 一切判断都以目标官方 commit 为基线，不在已经偏离的脏树上继续补丁。

这是硬约束，不是建议。

## 4. 永久边界

必须遵守：

1. 基线永远是官方 Hermes 指定 commit。
2. 每个 release 都必须从目标官方 commit 重新生成最小 patch。
3. 不在旧的本地汉化结果上继续叠补丁。
4. 不改控制流，不改缩进结构，不改条件块，不改运行路径。
5. 每一行源码改动都必须能直接追溯到“终端或 Telegram 的固定可见中文化需求”。

默认禁止：

- 新建自动维护系统
- 定时任务、LaunchAgent、cron、自愈链路
- 失败包上报链路
- Web UI 汉化
- 翻译 LLM 生成内容
- 改写发给模型的内部提示文本
- 为了“便于汉化”而扩大源码改动面
- 在维护过程中顺手做源码重构

## 5. 当前架构结论

这是过去多轮协作后得到的硬结论，后续维护不要倒退：

1. **外置词条优先，源码只保留最薄钩子。**
2. **不要再依赖可执行的本地化运行时桥。**
3. **本地化数据应优先是 YAML 等只读数据，而不是执行 `~/.hermes/localization/*.py`。**
4. **测试应覆盖当前真实路径，不要保留已经脱离实际实现的“历史回归测试”。**

特别注意：

- 当前 release 不应再发布 `localization/hermes_zh_runtime.py` 之类的运行时桥。
- `scripts/verify_release.py` 必须阻止 `localization_files` 中出现 Python 运行时文件。
- 如果维护时发现旧本地安装残留这类文件，只能在安装脚本中清理它，不能继续依赖或扩展它。

## 6. 仓库内关键文件

- `release.json`
  当前发布索引；`latest_release` 指向默认发布版本。
- `releases/<release>/manifest.json`
  当前 release 的元数据、允许修改的源码文件列表、词条文件列表。
- `releases/<release>/localization/*`
  外置词条文件。未来 release 默认优先使用这类数据文件。
- `releases/<release>/skins/*`
  该版本随 release 分发的自建皮肤 YAML。
- `releases/<release>/patches/hermes-zh.patch`
  该官方 commit 对应的最小源码 patch。
- `scripts/apply_release.py`
  用户安装/更新入口。
- `scripts/verify_release.py`
  版本一致性与本地状态校验入口。

## 7. 官方更新后的正确顺序

**先对齐官方基线，再做新的中文包。不要反过来。**

正确顺序：

1. 确定目标官方 commit。
2. 准备一棵干净的 Hermes 官方基线树。
   最好在独立 scratch worktree 或全新检出里做，不要直接在旧汉化脏树上做。
3. 对比旧官方 commit 与新官方 commit。
4. 只检查终端和 Telegram 范围内的固定可见文案是否新增、变更或删除。
5. 先复用旧 release 的词条与皮肤，但逐项核对是否仍然适用。
6. 优先更新外置词条文件。
7. 外置词条无法覆盖时，才做最小源码接线或字符替换。
8. 重新生成新的 `hermes-zh.patch`。
9. 生成新的 `releases/<new_release>/`。
10. 运行校验与 smoke test。
11. 全部通过后，才更新 `release.json` 的 `latest_release`。

注意：

- 这里的 `latest_release` 是“本仓库当前发布的最新中文包版本”。
- 它不等于“官方 Hermes 当前最新版本”。
- 只有当新一版中文包已经做完、校验通过、远端也同步后，才能把它称为本仓库的“最新 release”。

不要这样做：

- 不要先改中文包仓库，再倒推 Hermes。
- 不要在旧 patch 或旧脏树上继续叠补丁。
- 不要直接复制旧 patch 当成新 patch 而不重新生成。

## 8. 接手时先检查什么

每次接手前，先检查这 6 件事：

1. 当前 `release.json` 指向哪个 release。
2. 该 release 对应哪个官方 commit。
3. 本地用于维护的 Hermes 源码是否已经回到这个目标官方 commit。
4. 旧 release 中哪些词条和皮肤可以直接复用。
5. 官方这次更新是否真的触及终端 / Telegram 固定可见文案。
6. 历史 release 中是否残留不应继续继承的旧实现痕迹。

然后再额外检查 3 件事：

7. 本地 Hermes 基线 commit、当前 release 的 `official_commit`、远端 release 仓库状态是否已经是同一版。
8. 本地 `scripts/verify_release.py --source-dir ~/.hermes/hermes-agent` 是否通过。
9. 如果不通过，错位发生在：
   - 本地 Hermes
   - 本地中文包 release
   - 远端中文包仓库
   这三者中的哪一层。

第 6 项尤其重要。
**历史存在，不代表未来应该继续照抄。**

## 9. 如何判断“这次官方更新需不需要继续汉化”

先看官方更新是否触及以下范围：

- CLI 启动页、提示语、状态输出
- slash 命令注释与成功/失败提示
- 终端中的固定 spinner、status、notice 文案
- 终端各皮肤固定欢迎语、帮助头、固定思考状态提示语
- Telegram slash 命令注释
- Telegram 中非 LLM 生成的固定提示语

检查时必须按“类别”扫，不要按截图扫。至少覆盖这些类别：

- 启动页：版本行、更新提示、可用工具、MCP、可用技能、欢迎语、底部提示。
- slash 命令元数据：`/help`、补全菜单、命令注释、命令分类。
- slash 命令执行反馈：必须按“固定回复 + 回复中的固定词”完整检查，不只检查命令注释。终端侧至少覆盖 `/new`、`/reset`、`/status`、`/profile`、`/config`、`/history`、`/resume`、`/branch`、`/save`、`/retry`、`/undo`、`/model`、`/provider`、`/personality`、`/yolo`、`/snapshot`、`/skills`、skill slash command、`/reload-mcp`、`/browser`、`/queue`、`/background`、`/btw`、`/stop`、`/image`、`/paste`、`/reasoning`、`/fast`、`/compress`、`/usage`、`/insights`、`/voice`、插件/快捷命令等固定输出。
- Telegram slash 命令执行反馈：至少覆盖 `/new`、`/reset`、`/status`、`/commands`、`/help`、`/model`、`/provider`、`/personality`、`/retry`、`/undo`、`/sethome`、`/voice`、`/rollback`、`/background`、`/btw`、`/reasoning`、`/fast`、`/yolo`、`/verbose`、`/compress`、`/title`、`/resume`、`/branch`、`/usage`、`/insights`、`/reload-mcp`、`/approve`、`/deny`、`/update`、`/debug` 等固定输出。
- 二级/空状态提示：没有快照、没有插件、没有后台进程、没有会话数据库、没有历史消息、没有可分叉对话、没有已认证 provider、缺少参数、未知子命令、最近项提示、命令成功后的确认行、命令失败后的固定前缀。
- 用户输入后到 LLM 回复前：agent 初始化、busy command status、spinner thinking verbs、记忆/检索短状态行。
- 皮肤：全部内置皮肤和本仓库自建皮肤的 welcome、goodbye、help header、thinking verbs。
- Telegram：命令菜单描述、slash 命令执行反馈、按钮/确认提示、非 LLM 生成的状态消息。

典型遗漏信号包括但不限于：

- `YOLO mode ON`
- `No state snapshots yet`
- `Loading skill:`
- `[SYSTEM: The user has invoked ...]` 被直接展示给用户
- `reasoning...`、`formulating...`、`cogitating...`、`brainstorming...`
- `Searching skills...`、`Reloading MCP servers...`

如果官方更新没有触及这些范围，仍然可以发布一个新 release 绑定新的官方 commit，但原则是：

- patch 仍然必须基于新的官方 commit 重新生成
- 不允许直接在旧 release 上“假设兼容”
- 不允许为了凑新 release 而顺手扩大改动面

## 10. 汉化时的优先级

按这个顺序做：

1. 外置词条替换
2. 外置皮肤词条
3. 极小源码字符替换
4. 极小源码接线
5. 仅在绝对必要时做极小显示层适配

第 5 条例外必须非常少。
当前已知可以接受的例子是：

- 为了中文宽字符显示正确，做极小的终端显示宽度适配

这类例外必须同时满足：

- 只影响显示层
- 不改变业务逻辑
- 不改变会话、命令分发、状态机或模型交互
- 能在 `manifest.json` 中明确解释

## 11. 源码改动的允许形态

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

## 12. 审计标准

每次维护完成后，必须重新做一轮“基线审计”。

审计时，逐个对照官方 commit 判断：

1. 这个文件为什么与官版不同？
2. 这处不同是否属于终端 / Telegram 固定可见中文化？
3. 这处不同能不能外置到数据层？
4. 如果不能外置，是否已经是最薄钩子？
5. 是否改变了控制流、运行路径、状态机或模型交互？
6. 这条改动是否是“整类问题”的解决，而不是某个表面症状的补丁？

如果答不清楚，就说明改动还不够收口。

## 13. 验证与 smoke test

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

## 14. 常见错误做法

以下做法过去都证明会把事情搞复杂，未来不要再犯：

1. 在已经汉化过的脏树上继续修补，而不是回到官方基线重做。
2. 用户指出一个问题，就只修那一个截图、那一个皮肤、那一句提示，而不检查整类范围。
3. 把本地化做成可执行运行时桥，而不是只读数据。
4. 为了修一个文案问题，顺手扩大到结构重构。
5. 保留已经不再对应真实代码路径的旧测试或旧说明。
6. 不做验证就宣称“全部完成”。

## 15. manifest 与 release 产物规则

`manifest.json` 不是摆设，必须真实反映当前 release：

- `allowed_source_files` 只列当前 release 真正允许改动的源码文件
- `localization_files` 只列当前 release 真正需要的词条文件
- `justified_non_text_logic` 只列真正必要的显示层例外

如果某个历史 release 的 manifest 里还有旧实现痕迹：

- 不要把它当成未来 release 的模板直接复制
- 先判断它是不是历史遗留
- 能收口就收口
- 不能立即收口，也要在文档里明确标注为历史遗留，而不是默认标准

## 16. 提交前最后自检

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

## 17. 新线程更新任务的默认工作流

如果你是一个没有上下文的新线程 LLM Agent，而用户让你“更新 Hermes”或“检查 Hermes 与中文包是否一致”，默认按下面的顺序执行。

不要先假设用户要追官方最新。
先判断用户要的是下面哪一种：

### 场景 A：只要求三者一致

目标：

- 本地 Hermes
- 本地中文包
- 远端中文包仓库

三者都绑定在同一版 Hermes 上，并且彼此一致。

这时先做：

1. 读取 `release.json`。
2. 读取当前 release 的 `manifest.json`。
3. 检查本地 `~/.hermes/hermes-agent` 的 `HEAD`。
4. 运行：
   `python3 ~/.hermes/hermes-zh-overlay-release/scripts/verify_release.py --source-dir ~/.hermes/hermes-agent`
5. 检查本地中文包仓库 `HEAD` 是否等于远端 `origin/main`。

如果这几项都成立，就不要为了追官方最新而继续改动。

### 场景 B：要求升级到新的官方版本

只有当用户明确要求“升级到官方新版本”时，才进入升级流程。

这时再做：

1. 确认官方目标 commit。
2. 从该官方 commit 干净基线开始。
3. 判断终端 / Telegram 固定可见文案是否进入新的汉化范围。
4. 先复用旧 release 的词条与皮肤。
5. 外置优先，源码最小。
6. 重新生成 patch / manifest / release。
7. 验证通过后，再同步远端。

### 给新线程 Agent 的硬要求

如果任务是“更新 Hermes”或“检查一致性”，你必须在汇报里明确回答：

1. 当前 release 是哪一版。
2. 本地 Hermes 基线 commit 是哪一版。
3. 远端中文包仓库当前 release / HEAD 是哪一版。
4. 三者现在是否一致。
5. 如果不一致，错位在哪一层。
6. 你本次有没有真的升级到新的官方版本，还是只是在收口三者一致。

禁止：

- 把“用户要三者一致”误解成“用户一定要追官方最新”
- 没跑 `verify_release.py` 就口头宣称一致
- 只看本地、不看远端
- 只看 commit、不看 patch / manifest / verify
