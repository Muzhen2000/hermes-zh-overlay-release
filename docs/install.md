# 安装说明

这里的“安装”指把这个 release 系统检出到本地并用于维护/验证，不是安装 Hermes 本体。

## 先决条件

- macOS
- `git`
- `python3`
- 已安装 Hermes，且源码目录位于 `~/.hermes/hermes-agent`

## 一行安装

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/install_local_overlay.py | python3 -
```

这条命令会：

- 把 release 仓库安装到 `~/.hermes/hermes-zh-overlay-release`
- 安装本地维护器到 `~/.hermes/scripts/hermes_zh_overlay_manager.py`
- 安装支持策略到 `~/.hermes/localization/support-policy.json`
- 写入 `~/Library/LaunchAgents/com.muzhen.hermes-zh-overlay-maintain.plist`
- 默认立即运行一次 `maintain`，之后由 launchd 定期维护

如果你只想安装系统、不立即改动 Hermes 源码，可以运行：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/install_local_overlay.py | python3 - --no-maintain
```

如果你只想测试安装流程、不注册 launchd：

```bash
curl -fsSL https://raw.githubusercontent.com/Muzhen2000/hermes-zh-overlay-release/main/scripts/install_local_overlay.py | python3 - --no-bootstrap --no-maintain
```

## 本地验收

安装后运行：

```bash
python3 ~/.hermes/scripts/hermes_zh_overlay_manager.py status
```

你应该看到：

- `supported_commit=...`
- `overlay_present=yes`
- `scan missing=0 ... control=0`

如果本地维护失败，会自动生成失败包：

```text
~/Desktop/Hermes-ZH-Failures/latest
```

把这个目录交给新的 Codex 线程即可继续排查。

## 维护者本地准备

```bash
git clone https://github.com/Muzhen2000/hermes-zh-overlay-release.git
cd hermes-zh-overlay-release
python3 -m pytest tests -q
```

仓库里的本地维护 payload 有两个核心文件：

- `payload/localization/support-policy.json`
- `payload/scripts/hermes_zh_overlay_manager.py`

前者声明当前受支持的 Hermes 官方 commit，后者是在用户本地执行“保持受支持版本、重铺 overlay、复扫验证”的维护器实现。

## 本地检查

你可以直接运行这些脚本验证 release 逻辑：

- `python3 scripts/check_upstream.py`
- `python3 scripts/build_candidate.py`
- `python3 scripts/validate_candidate.py --overlay-ok --tests-ok --scan-missing 0 --scan-control 0`
- `python3 scripts/collect_failure_bundle.py`
- `python3 scripts/install_local_overlay.py --no-bootstrap --no-maintain`

这些脚本都是仓库级维护工具，不会修改 Hermes 的用户配置、记忆或会话数据。

如果你要核对“本地 Hermes 应该跟随哪个 commit”，看 `release.json` 和 `payload/localization/support-policy.json`；本地维护器必须以这里声明的 `supported_commit` 为准，而不是盲目追 `origin/main`。
