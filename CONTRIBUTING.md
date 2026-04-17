# CONTRIBUTING

这个仓库只接受“版本绑定的最小中文包”改动。

## 基线

- 先锁定一个官方 Hermes commit
- 所有改动都从这个官方 commit 重新比较
- 不在旧 patch 上继续叠补丁

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

## 源码改动标准

- 优先外置词条
- 源码只保留最小钩子
- 如需改逻辑，必须能证明是中文显示本身所必需
- `manifest.json` 中要列出全部允许改动文件

## 提交前检查

- patch 只触达 `manifest.json` 允许的源码文件
- `python3 -m pytest tests`
- `python3 scripts/verify_release.py`
