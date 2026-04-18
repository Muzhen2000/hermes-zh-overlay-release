from __future__ import annotations

import importlib.util
import subprocess
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
        "tests/cli/test_cli_loading_indicator.py",
        "tests/cli/test_cli_localized_feedback.py",
        "tests/gateway/test_localized_slash_replies.py",
        "tests/hermes_cli/test_commands.py",
        "tests/hermes_cli/test_skin_engine.py",
    ]


def test_release_json_points_to_existing_release():
    module = _load_module()
    release_id, release_index, manifest = module._load_metadata(ROOT)

    assert release_id == release_index["latest_release"]
    assert manifest["release"] == release_id


def test_changed_files_includes_worktree_staged_and_untracked_files(tmp_path):
    module = _load_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "tracked.txt").write_text("old\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)

    (repo / "tracked.txt").write_text("new\n", encoding="utf-8")
    (repo / "staged.txt").write_text("staged\n", encoding="utf-8")
    subprocess.run(["git", "add", "staged.txt"], cwd=repo, check=True)
    (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")

    assert module._changed_files(repo) == ["staged.txt", "tracked.txt", "untracked.txt"]
