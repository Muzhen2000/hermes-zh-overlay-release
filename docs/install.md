# 安装说明

这里的“安装”指把这个 release 系统检出到本地并用于维护/验证，不是安装 Hermes 本体。

## 先决条件

- macOS
- `git`
- `python3`
- `gh`

## 本地准备

```bash
git clone https://github.com/Muzhen2000/hermes-zh-overlay-release.git
cd hermes-zh-overlay-release
python3 -m pytest tests -q
```

## 远端部署

1. 把 `main` 推到 GitHub。
2. 在仓库上触发 `unattended-release` workflow。
3. 如果失败，先看 artifact 里的 failure bundle，再看桌面镜像：
   `~/Desktop/Hermes-ZH-Failures/latest`

## 本地检查

你可以直接运行这些脚本验证 release 逻辑：

- `python3 scripts/check_upstream.py`
- `python3 scripts/build_candidate.py`
- `python3 scripts/validate_candidate.py --overlay-ok --tests-ok --scan-missing 0 --scan-control 0`
- `python3 scripts/collect_failure_bundle.py`

这些脚本都是仓库级维护工具，不会修改 Hermes 的用户配置、记忆或会话数据。

