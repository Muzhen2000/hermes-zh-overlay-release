# AGENTS

本仓库负责 Hermes Discord 斜杠命令的中文本地化。

## 汉化范围

**只汉化 Discord 斜杠命令：**
- 命令名称（如 `/新会话`、`/重置`）
- 命令描述（如 "开始新会话"）
- 触发命令后的固定回复（如 "新会话已开始~"）

**不汉化：**
- 终端界面
- 皮肤/主题
- 其他平台

## 更新流程

1. 拉取官方最新版本：`git fetch origin`
2. 确定新 commit：`git log --oneline origin/main | head -1`
3. 创建新 release 目录
4. 生成只含 Discord 斜杠命令的汉化补丁
5. 更新 manifest.json
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
