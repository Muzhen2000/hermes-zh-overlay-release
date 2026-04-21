from __future__ import annotations

import json
import re
from pathlib import Path
import importlib.util
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _latest_release() -> str:
    release_index = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
    return str(release_index["latest_release"])


def test_release_index_scope_includes_feishu():
    release_index = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))

    assert release_index["scope"] == ["terminal", "telegram", "feishu"]
    assert release_index["web_ui_policy"] == "upstream-only"


def test_manifest_lists_existing_localization_files():
    release_id = _latest_release()
    manifest = json.loads(
        (ROOT / "releases" / release_id / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / release_id / "localization"

    for name in manifest["localization_files"]:
        assert (release_dir / name).exists()


def test_release_does_not_ship_legacy_runtime_bridge():
    release_id = _latest_release()
    manifest = json.loads(
        (ROOT / "releases" / release_id / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / release_id / "localization"

    assert "hermes_zh_runtime.py" not in manifest["localization_files"]
    assert not (release_dir / "hermes_zh_runtime.py").exists()


def test_real_ui_catalog_covers_all_static_runtime_keys():
    release_id = _latest_release()
    manifest = json.loads(
        (ROOT / "releases" / release_id / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / release_id
    ui_data = yaml.safe_load((release_dir / "localization" / "ui.zh-CN.yaml").read_text(encoding="utf-8"))
    messages = set((ui_data or {}).get("messages", {}))
    patch_text = (release_dir / manifest["patch"]).read_text(encoding="utf-8")
    added_source = "\n".join(
        line[1:]
        for line in patch_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )

    helper_prefixes = {
        "cli.py": (("_cli_ui", "cli."),),
        "gateway/run.py": (("_gateway_ui", "gateway.runtime."),),
        "gateway/platforms/telegram.py": (("_tg_ui", "gateway.telegram."),),
        "gateway/platforms/feishu.py": (("_feishu_ui", "gateway.feishu."),),
        "hermes_cli/gateway.py": (("_ui", "gateway."),),
        "hermes_cli/auth.py": (("_ui", "auth."),),
        "hermes_cli/debug.py": (("_ui", "debug."),),
        "hermes_cli/main.py": (("_ui", "main."),),
        "hermes_cli/status.py": (("_ui", "status."),),
        "hermes_cli/banner.py": (("_ui", "banner."),),
    }

    expected_keys = set()
    current_file = ""
    for line in patch_text.splitlines():
        if line.startswith("diff --git a/"):
            parts = line.split()
            current_file = parts[3][2:] if len(parts) >= 4 and parts[3].startswith("b/") else ""
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added_line = line[1:]
        for helper, prefix in helper_prefixes.get(current_file, ()):
            pattern = rf"{re.escape(helper)}\(\s*[\"']([^\"']+)[\"']"
            for match in re.findall(pattern, added_line):
                expected_keys.add(f"{prefix}{match}")

    missing = sorted(expected_keys - messages)
    assert not missing


def test_manifest_lists_existing_skin_files():
    release_id = _latest_release()
    manifest = json.loads(
        (ROOT / "releases" / release_id / "manifest.json").read_text(encoding="utf-8")
    )
    skins_dir = ROOT / "releases" / release_id / "skins"

    for name in manifest["skin_files"]:
        assert (skins_dir / name).exists()


def test_manifest_keeps_terminal_localization_entrypoints_under_management():
    release_id = _latest_release()
    manifest = json.loads(
        (ROOT / "releases" / release_id / "manifest.json").read_text(encoding="utf-8")
    )

    for path in ["hermes_cli/auth.py", "hermes_cli/debug.py", "hermes_cli/main.py"]:
        assert path in manifest["allowed_source_files"]


def test_skin_localization_covers_builtins_and_release_custom_skins():
    release_id = _latest_release()
    manifest = json.loads(
        (ROOT / "releases" / release_id / "manifest.json").read_text(encoding="utf-8")
    )
    skins_data = yaml.safe_load(
        (ROOT / "releases" / release_id / "localization" / "skins.zh-CN.yaml").read_text(encoding="utf-8")
    )
    localized = set((skins_data or {}).get("skins", {}).keys())
    builtin = {
        "default",
        "ares",
        "charizard",
        "daylight",
        "mono",
        "poseidon",
        "sisyphus",
        "slate",
        "warm-lightmode",
    }
    shipped_custom = {name.removesuffix(".yaml") for name in manifest["skin_files"]}

    assert builtin.issubset(localized)
    assert shipped_custom.issubset(localized)

    for skin_name in builtin | shipped_custom:
        skin = skins_data["skins"][skin_name]
        verbs = (skin.get("spinner") or {}).get("thinking_verbs") or []
        assert verbs, f"{skin_name} must define localized thinking_verbs"


def test_latest_ui_catalog_covers_banner_toolset_aliases():
    release_id = _latest_release()
    ui_data = yaml.safe_load(
        (ROOT / "releases" / release_id / "localization" / "ui.zh-CN.yaml").read_text(encoding="utf-8")
    )
    messages = (ui_data or {}).get("messages", {})

    for key in (
        "banner.toolset.discord",
        "banner.toolset.feishu_doc",
        "banner.toolset.feishu_drive",
    ):
        assert key in messages


def test_local_scan_script_tracks_current_runtime_helpers():
    scan_script = ROOT.parent / "scripts" / "scan_hermes_localization.py"
    spec = importlib.util.spec_from_file_location("scan_hermes_localization", scan_script)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    ui_hooks = {(Path(hook.path).name, hook.helper, hook.prefix) for hook in module.UI_HOOKS}
    assert ("auth.py", "_ui", "auth.") in ui_hooks
    assert ("debug.py", "_ui", "debug.") in ui_hooks
    assert ("main.py", "_ui", "main.") in ui_hooks

    hermes_root = ROOT.parent / "hermes-agent"
    allowlist = module.CONTROL_AUDIT_ALLOWLIST
    assert "_ui" in allowlist[str(hermes_root / "hermes_cli" / "auth.py")]
    assert "_ui" in allowlist[str(hermes_root / "hermes_cli" / "debug.py")]
    assert "_ui" in allowlist[str(hermes_root / "hermes_cli" / "main.py")]
