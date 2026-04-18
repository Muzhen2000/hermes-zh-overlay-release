from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_release_index_scope_is_terminal_and_telegram_only():
    release_index = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))

    assert release_index["scope"] == ["terminal", "telegram"]
    assert release_index["web_ui_policy"] == "upstream-only"


def test_manifest_lists_existing_localization_files():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / "31e72764" / "localization"

    for name in manifest["localization_files"]:
        assert (release_dir / name).exists()


def test_release_does_not_ship_legacy_runtime_bridge():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / "31e72764" / "localization"

    assert "hermes_zh_runtime.py" not in manifest["localization_files"]
    assert not (release_dir / "hermes_zh_runtime.py").exists()


def test_real_ui_catalog_covers_all_static_runtime_keys():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / "31e72764"
    ui_data = yaml.safe_load((release_dir / "localization" / "ui.zh-CN.yaml").read_text(encoding="utf-8"))
    messages = set((ui_data or {}).get("messages", {}))
    patch_text = (release_dir / manifest["patch"]).read_text(encoding="utf-8")
    added_source = "\n".join(
        line[1:]
        for line in patch_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )

    expected_keys = set()
    expected_keys.update(f"cli.{match}" for match in re.findall(r"_cli_ui\(\s*[\"']([^\"']+)[\"']", added_source))
    expected_keys.update(
        f"gateway.runtime.{match}"
        for match in re.findall(r"_gateway_ui\(\s*[\"']([^\"']+)[\"']", added_source)
    )

    missing = sorted(expected_keys - messages)
    assert not missing


def test_manifest_lists_existing_skin_files():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )
    skins_dir = ROOT / "releases" / "31e72764" / "skins"

    for name in manifest["skin_files"]:
        assert (skins_dir / name).exists()


def test_manifest_keeps_terminal_localization_entrypoints_under_management():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )

    for path in ["hermes_cli/auth.py", "hermes_cli/debug.py", "hermes_cli/main.py"]:
        assert path in manifest["allowed_source_files"]


def test_skin_localization_covers_builtins_and_release_custom_skins():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )
    skins_data = yaml.safe_load(
        (ROOT / "releases" / "31e72764" / "localization" / "skins.zh-CN.yaml").read_text(encoding="utf-8")
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
