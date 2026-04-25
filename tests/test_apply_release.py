from __future__ import annotations

import importlib.util
import json
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

    if result["patch_path"]:
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
    legacy_runtime = hermes_home / "localization" / "hermes_zh_runtime.py"
    legacy_runtime_cache = hermes_home / "localization" / "__pycache__" / "hermes_zh_runtime.cpython-314.pyc"
    baseline_report = hermes_home / "localization" / "reports" / "hermes-zh-baseline.json"
    legacy_patch = hermes_home / "localization" / "patches" / "hermes-zh-overlay.patch"
    legacy_plist = user_home / "Library" / "LaunchAgents" / "com.muzhen.hermes-zh-overlay-maintain.plist"

    for path in [
        legacy_manager,
        legacy_support,
        legacy_runtime,
        legacy_runtime_cache,
        baseline_report,
        legacy_patch,
        legacy_plist,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")

    removed = module._prune_legacy_overlay(hermes_home, user_home)

    assert str(legacy_manager) in removed
    assert str(legacy_support) in removed
    assert str(legacy_runtime) in removed
    assert str(legacy_runtime_cache.parent) in removed
    assert str(legacy_patch) in removed
    assert str(legacy_plist) in removed
    assert not legacy_manager.exists()
    assert not legacy_support.exists()
    assert not legacy_runtime.exists()
    assert not legacy_runtime_cache.parent.exists()
    assert baseline_report.exists()
    assert not legacy_patch.exists()
    assert not legacy_plist.exists()


def test_invalidate_update_cache_removes_default_and_profile_caches(tmp_path):
    module = _load_module()
    hermes_home = tmp_path / ".hermes"
    default_cache = hermes_home / ".update_check"
    ops_cache = hermes_home / "profiles" / "ops" / ".update_check"
    dev_cache = hermes_home / "profiles" / "dev" / ".update_check"

    for path in [default_cache, ops_cache, dev_cache]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"ts":1,"behind":279}', encoding="utf-8")

    removed = module._invalidate_update_cache(hermes_home)

    assert str(default_cache) in removed
    assert str(ops_cache) in removed
    assert str(dev_cache) in removed
    assert not default_cache.exists()
    assert not ops_cache.exists()
    assert not dev_cache.exists()


def test_apply_release_prints_visible_progress(monkeypatch, tmp_path, capsys):
    module = _load_module()
    hermes_home = tmp_path / ".hermes"
    repo_root = tmp_path / "overlay"
    release_dir = repo_root / "releases" / "r1"
    (release_dir / "localization").mkdir(parents=True, exist_ok=True)
    (release_dir / "patches").mkdir(parents=True, exist_ok=True)
    (release_dir / "skins").mkdir(parents=True, exist_ok=True)
    (repo_root / "release.json").write_text(
        json.dumps(
            {
                "official_repo": "https://github.com/example/hermes-agent.git",
                "latest_release": "r1",
                "scope": ["terminal", "discord"],
                "web_ui_policy": "upstream-only",
            }
        ),
        encoding="utf-8",
    )
    (release_dir / "manifest.json").write_text(
        json.dumps(
            {
                "release": "r1",
                "official_commit": "deadbeef",
                "scope": ["terminal", "discord"],
                "web_ui_policy": "upstream-only",
                "patch": "",
                "localization_files": ["ui.zh-CN.yaml"],
                "skin_files": [],
                "allowed_source_files": [],
            }
        ),
        encoding="utf-8",
    )
    (release_dir / "localization" / "ui.zh-CN.yaml").write_text("messages: {}\n", encoding="utf-8")
    (release_dir / "patches" / "hermes-zh.patch").write_text("", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "_clone_or_update_release_repo",
        lambda **kwargs: repo_root,
    )
    monkeypatch.setattr(
        module,
        "_copy_release_assets",
        lambda **kwargs: {
            "changed": {"ui.zh-CN.yaml": True, "hermes-zh-r1.patch": True},
            "patch_path": "",
        },
    )
    monkeypatch.setattr(module, "_prune_legacy_overlay", lambda *args, **kwargs: [])
    monkeypatch.setattr(module, "_align_source_to_official", lambda **kwargs: None)
    def fail_if_patch_called(**kwargs):
        raise AssertionError("_apply_patch should not run for no-patch releases")

    monkeypatch.setattr(module, "_apply_patch", fail_if_patch_called)
    monkeypatch.setattr(module, "_invalidate_update_cache", lambda *args, **kwargs: [])

    module.apply_release(hermes_home=hermes_home, release_source_dir=repo_root)

    progress = capsys.readouterr().err
    assert "[hermes-zh-release] 同步中文包仓库" in progress
    assert "[hermes-zh-release] 对齐官方 Hermes 源码版本" in progress
    assert "[hermes-zh-release] 无中文源码 patch，保持官方源码不变" in progress
