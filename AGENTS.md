# AGENTS

本仓库负责 Hermes Discord 和终端(TUI)斜杠命令的中文本地化。

## 汉化范围

**汉化 Discord 和终端的斜杠命令：**
- Discord：命令名称、描述、固定回复
- 终端(TUI)：命令名称、描述、固定回复

**不汉化：**
- 皮肤/主题
- 其他平台
- 工具说明

## 更新流程

1. 拉取官方最新版本：`git fetch origin`
2. 确定新 commit：`git log --oneline origin/main | head -1`
3. 在 hermes-agent 上做中文字符串替换
4. 生成 git diff 作为补丁
5. 创建新 release 目录和 manifest
6. 运行验证脚本
7. 推送远端

## 验证

```bash
python3 scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
```

## 应用

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$HOME/.hermes"
```
