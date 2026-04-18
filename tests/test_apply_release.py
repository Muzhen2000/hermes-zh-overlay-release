from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "apply_release.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("apply_release", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_copy_release_assets_materializes_expected_files(tmp_path):
    module = _load_module()
    hermes_home = tmp_path / ".hermes"
    release_id, _, manifest = module._load_release_metadata(ROOT)

    result = module._copy_release_assets(
        repo_root=ROOT,
        hermes_home=hermes_home,
        release_id=release_id,
        manifest=manifest,
    )

    assert Path(result["patch_path"]).exists()
    for name in manifest["localization_files"]:
        assert (hermes_home / "localization" / name).exists()
    for name in manifest["skin_files"]:
        assert (hermes_home / "skins" / name).exists()


def test_prune_legacy_overlay_removes_old_runtime_files(tmp_path):
    module = _load_module()
    hermes_home = tmp_path / ".hermes"
    user_home = tmp_path / "home"

    legacy_manager = hermes_home / "scripts" / "hermes_zh_overlay_manager.py"
    legacy_support = hermes_home / "localization" / "support-policy.json"
    legacy_reports = hermes_home / "localization" / "reports" / "old.json"
    legacy_patch = hermes_home / "localization" / "patches" / "hermes-zh-overlay.patch"
    legacy_plist = user_home / "Library" / "LaunchAgents" / "com.muzhen.hermes-zh-overlay-maintain.plist"

    for path in [legacy_manager, legacy_support, legacy_reports, legacy_patch, legacy_plist]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")

    removed = module._prune_legacy_overlay(hermes_home, user_home)

    assert str(legacy_manager) in removed
    assert str(legacy_support) in removed
    assert str(legacy_patch) in removed
    assert str(legacy_plist) in removed
    assert not legacy_manager.exists()
    assert not legacy_support.exists()
    assert not legacy_reports.exists()
    assert not legacy_patch.exists()
    assert not legacy_plist.exists()
