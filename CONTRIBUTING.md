# CONTRIBUTING

这个仓库只接受“版本绑定的最小中文包”改动。

## 基线

- 先锁定一个官方 Hermes commit
- 所有改动都从这个官方 commit 重新比较
- 不在旧 patch 上继续叠补丁
- 不在已经偏离官方的本地脏树上继续修补

## 范围

允许：

- 终端固定提示语
- Telegram 固定提示语
- slash 命令说明、成功提示、banner、spinner、tips、skills 展示文案

不允许：

- Web UI 汉化
- 与中文化无关的修复
- 自动维护、定时任务、失败包、远端自愈链路
- 无必要的控制流改动
- 只按一个截图或一个皮肤做症状修补
- 可执行本地化运行时桥

## 源码改动标准

- 优先外置词条
- 优先只读 YAML 数据，不新增执行 `localization/*.py` 的依赖
- 源码只保留最小钩子
- 如需改逻辑，必须能证明是中文显示本身所必需
- `manifest.json` 中要列出全部允许改动文件
- 每一行源码改动都必须能直接追溯到终端或 Telegram 的固定可见中文化需求

## 提交前检查

- patch 只触达 `manifest.json` 允许的源码文件
- `python3 scripts/verify_release.py`
- 推荐至少运行：
  - `python3 -m pytest tests/tools/test_skills_tool.py`
  - `python3 -m pytest tests/agent/test_display.py`
  - `python3 -m pytest tests/hermes_cli/test_skin_engine.py tests/hermes_cli/test_banner.py tests/hermes_cli/test_commands.py tests/hermes_cli/test_tips.py`
- 如果有测试因缺少可选依赖而无法运行，必须明确记录原因，不能当作“已通过”
