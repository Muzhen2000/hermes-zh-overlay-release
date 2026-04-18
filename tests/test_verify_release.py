from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_release.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_release", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_validate_release_matches_manifest_and_patch():
    module = _load_module()
    result = module.validate_release(ROOT)

    assert result["release"] == "31e72764"
    assert result["official_commit"] == "31e7276474976cd752d73de7701229eefd1b37ad"
    assert sorted(Path(path).name for path in result["skin_files"]) == [
        "bubblegum-80s.yaml",
        "lain.yaml",
        "mother.yaml",
        "mythos.yaml",
        "neonwave.yaml",
        "netrunner.yaml",
        "nous.yaml",
        "pirate.yaml",
        "sakura.yaml",
        "skynet.yaml",
        "vault-tec.yaml",
    ]
    assert sorted(result["patch_files"]) == [
        "agent/display.py",
        "agent/manual_compression_feedback.py",
        "cli.py",
        "gateway/platforms/telegram.py",
        "gateway/run.py",
        "hermes_cli/auth.py",
        "hermes_cli/banner.py",
        "hermes_cli/commands.py",
        "hermes_cli/debug.py",
        "hermes_cli/gateway.py",
        "hermes_cli/main.py",
        "hermes_cli/skin_engine.py",
        "hermes_cli/status.py",
        "hermes_cli/tips.py",
        "tests/tools/test_skills_tool.py",
        "tools/skills_tool.py",
    ]


def test_release_json_points_to_existing_release():
    module = _load_module()
    release_id, release_index, manifest = module._load_metadata(ROOT)

    assert release_id == release_index["latest_release"]
    assert manifest["release"] == release_id
