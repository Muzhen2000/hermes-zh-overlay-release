from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


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
    release_id, _, manifest = module._load_metadata(ROOT)

    assert result["release"] == release_id
    assert result["official_commit"] == manifest["official_commit"]
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
    assert sorted(result["patch_files"]) == sorted(manifest["allowed_source_files"])


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


def test_validate_release_rejects_missing_installed_skill_localization(tmp_path):
    module = _load_module()
    hermes_home = tmp_path / ".hermes"
    repo_root = hermes_home / "hermes-zh-overlay-release"
    release_dir = repo_root / "releases" / "r1"
    (release_dir / "localization").mkdir(parents=True, exist_ok=True)
    (release_dir / "patches").mkdir(parents=True, exist_ok=True)

    (repo_root / "release.json").write_text(
        json.dumps(
            {
                "official_repo": "https://github.com/example/hermes-agent.git",
                "latest_release": "r1",
                "web_ui_policy": "upstream-only",
                "scope": ["terminal", "telegram", "feishu"],
            }
        ),
        encoding="utf-8",
    )
    (release_dir / "manifest.json").write_text(
        json.dumps(
            {
                "release": "r1",
                "official_commit": "deadbeef",
                "scope": ["terminal", "telegram", "feishu"],
                "web_ui_policy": "upstream-only",
                "patch": "patches/hermes-zh.patch",
                "localization_files": ["skills.zh-CN.yaml", "ui.zh-CN.yaml"],
                "skin_files": [],
                "allowed_source_files": ["agent/skill_commands.py"],
            }
        ),
        encoding="utf-8",
    )
    (release_dir / "patches" / "hermes-zh.patch").write_text(
        "diff --git a/agent/skill_commands.py b/agent/skill_commands.py\n",
        encoding="utf-8",
    )
    (release_dir / "localization" / "ui.zh-CN.yaml").write_text(
        "messages: {}\n",
        encoding="utf-8",
    )
    (release_dir / "localization" / "skills.zh-CN.yaml").write_text(
        "skills: {}\ncategories: {}\n",
        encoding="utf-8",
    )

    skill_dir = hermes_home / "skills" / "codex"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: codex\ndescription: English description.\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(module.VerifyError, match="skills.zh-CN.yaml is missing installed skill descriptions"):
        module.validate_release(repo_root)
