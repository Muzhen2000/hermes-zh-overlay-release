# AGENTS

本仓库负责 Hermes Discord 和终端(TUI)斜杠命令的中文本地化。

## 汉化范围

**汉化 Discord 和终端的斜杠命令：**
- Discord：命令名称、描述、固定回复
- 终端(TUI)：命令名称（保留英文名为 alias）、描述、固定回复

**不汉化：**
- 皮肤/主题
- 其他平台（Telegram、Feishu、Web）
- 工具说明（tool descriptions）
- 模型提示词（prompts）
- 协议标识符和路由逻辑

## 关键约束

- Discord 命令名**必须全小写**（API 强制，大写导致网关崩溃）
- TUI 命令原英文名必须保留为 alias
- 内部路由标识（如 `"/reset"`）不翻译
- 补丁只做直接字符串替换，不引入 hook 架构

## 目录结构

```
releases/<commit>-<scope>/
  manifest.json          # 版本、基准、范围、补丁列表
  patches/*.patch        # 统一 diff 补丁
scripts/
  apply_release.py       # 一键应用 release
  verify_release.py      # 验证 release 完整性
release.json             # 当前最新 release 指针
```

## 更新流程

1. `cd ~/.hermes/hermes-agent && git fetch origin`
2. 确定新 commit：`git log --oneline origin/main | head -1`
3. 在 hermes-agent 上 checkout 新 commit，做中文字符串替换
4. `git diff` 生成补丁
5. 创建 release 目录 + manifest.json + 补丁文件
6. 更新 release.json / CHANGELOG.md / README.md / AGENTS.md
7. 验证：`git apply --check` + `verify_release.py`
8. 提交推送

## 验证

```bash
python3 scripts/verify_release.py --source-dir ~/.hermes/hermes-agent
```

## 应用

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/apply_release.py | python3 - --hermes-home "$HOME/.hermes"
```

## 维护 Skill

详细维护规范和翻译对照表在 `~/.claude/skills/hermes-zh/skill.md`。
