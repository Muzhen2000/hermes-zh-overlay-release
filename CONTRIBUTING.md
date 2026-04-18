# CONTRIBUTING

这个仓库只接受：**某一版官方 Hermes 对应的最小中文包**改动。

提交前先看：

- [AGENTS.md](./AGENTS.md)

## 范围

允许：

- 终端中用户可见、非 LLM 生成的固定文案
- Telegram 中用户可见、非 LLM 生成的固定文案
- 与上述中文化直接相关的最小 patch、词条、皮肤、manifest、release 元数据

不允许：

- Web UI 汉化
- LLM 回答正文汉化
- 与中文化无关的修复、重构、顺手优化
- 任何旧自动维护系统的重新引入；历史相关内容只允许作为残留清理对象存在

## 改动标准

- 先锁定目标官方 commit
- 必须从该官方基线出发，不在旧脏树上继续补丁
- 优先外置词条和皮肤
- 非必要不改源码
- 必要时也只允许最小、可追溯到用户可见中文化需求的源码改动
- 不改控制流、不改条件块、不扩散到无关区域

## 提交前校验

- `python3 scripts/verify_release.py --source-dir ~/.hermes/hermes-agent`
- patch 只触达当前 release 允许的源码文件
- 如本次触及终端显示或命令文案，至少补跑相关 CLI 测试

如果你是未来继续维护的 LLM Agent，不要只看这个文件，必须先完整阅读 `AGENTS.md`。
