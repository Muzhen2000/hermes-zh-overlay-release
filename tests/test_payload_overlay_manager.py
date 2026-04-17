from __future__ import annotations

import json
import importlib.util
import plistlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "payload" / "scripts" / "hermes_zh_overlay_manager.py"


def _load_manager_module():
    spec = importlib.util.spec_from_file_location("payload_overlay_manager", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_payload_manager_refreshes_empty_patch_before_noop_when_overlay_present(tmp_path, monkeypatch):
    manager = _load_manager_module()
    patch_file = tmp_path / "hermes-zh-overlay.patch"
    patch_file.write_text("", encoding="utf-8")
    calls = []

    monkeypatch.setattr(manager, "PATCH_FILE", patch_file, raising=False)
    monkeypatch.setattr(manager, "_ensure_dirs", lambda: None, raising=False)
    monkeypatch.setattr(
        manager,
        "_load_support_policy",
        lambda: {
            "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
            "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
            "maintenance_interval_seconds": 21600,
        },
        raising=False,
    )
    monkeypatch.setattr(manager, "_assert_supported_origin", lambda policy: None, raising=False)
    monkeypatch.setattr(manager, "_git_status", lambda: {"hermes_cli/main.py": " M"}, raising=False)
    monkeypatch.setattr(manager, "_unexpected_paths", lambda status_map: [], raising=False)
    monkeypatch.setattr(manager, "_unstage_managed_paths", lambda status_map: None, raising=False)
    monkeypatch.setattr(manager, "_overlay_present", lambda status_map: True, raising=False)
    monkeypatch.setattr(manager, "_fetch_upstream", lambda remote: None, raising=False)
    monkeypatch.setattr(manager, "_commit_exists", lambda ref: True, raising=False)
    monkeypatch.setattr(manager, "_pending_commits", lambda ref: 0, raising=False)
    monkeypatch.setattr(
        manager,
        "_generate_patch_text",
        lambda: calls.append(("generate_patch", None)) or "PATCH\n",
        raising=False,
    )
    monkeypatch.setattr(manager, "_sync_launchd_schedule_from_policy", lambda: calls.append(("sync_launchd", None)), raising=False)

    class _Completed:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append(tuple(cmd))
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _Completed("01906e99dd225b7946c770479fcd9cc2949e7104\n")
        return _Completed("")

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    exit_code = manager.cmd_maintain(type("Args", (), {"scheduled": False})())

    assert exit_code == 0
    assert ("generate_patch", None) in calls
    assert patch_file.read_text(encoding="utf-8") == "PATCH\n"


def test_payload_manager_restores_previous_launchd_plist_when_bootstrap_fails(tmp_path, monkeypatch):
    manager = _load_manager_module()
    policy = tmp_path / "support-policy.json"
    policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 3600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    plist_path = tmp_path / "com.muzhen.hermes-zh-overlay-maintain.plist"
    original_plist = {
        "Label": "com.muzhen.hermes-zh-overlay-maintain",
        "ProgramArguments": ["/usr/bin/python3", "manager.py", "maintain", "--scheduled"],
        "StartInterval": 21600,
    }
    plist_path.write_bytes(plistlib.dumps(original_plist))
    monkeypatch.setattr(manager, "SUPPORT_POLICY_FILE", policy, raising=False)
    monkeypatch.setattr(manager, "LAUNCHD_PLIST_PATH", plist_path, raising=False)
    monkeypatch.setattr(manager.os, "getuid", lambda: 501, raising=False)

    calls = []

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append(cmd)
        if cmd == ["launchctl", "bootstrap", "gui/501", str(plist_path)] and len(calls) == 2:
            raise manager.OverlayError("bootstrap failed")
        return type("Completed", (), {"stdout": "", "stderr": "", "returncode": 0})()

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    with pytest.raises(manager.OverlayError, match="bootstrap failed"):
        manager._sync_launchd_schedule_from_policy()

    payload = plistlib.loads(plist_path.read_bytes())
    assert payload["StartInterval"] == 21600
    assert calls == [
        ["launchctl", "bootout", "gui/501/com.muzhen.hermes-zh-overlay-maintain"],
        ["launchctl", "bootstrap", "gui/501", str(plist_path)],
        ["launchctl", "bootstrap", "gui/501", str(plist_path)],
    ]


def test_payload_manager_writes_failure_bundle_to_desktop_when_maintain_fails(tmp_path, monkeypatch):
    manager = _load_manager_module()
    bundle_dir = tmp_path / "failure-bundle"
    desktop_dir = tmp_path / "Desktop"

    monkeypatch.setattr(manager, "LOCAL_FAILURE_BUNDLE_DIR", bundle_dir, raising=False)
    monkeypatch.setattr(manager, "DESKTOP_DIR", desktop_dir, raising=False)
    monkeypatch.setattr(manager, "LATEST_SCAN_FILE", tmp_path / "missing-scan.json", raising=False)
    monkeypatch.setattr(manager, "_head_short", lambda: "deadbee", raising=False)
    monkeypatch.setattr(
        manager,
        "_load_support_policy",
        lambda: {
            "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
            "supported_commit": "abc123",
            "maintenance_interval_seconds": 21600,
        },
        raising=False,
    )

    def _failing_maintain(_args):
        raise manager.OverlayError("synthetic maintain failure")

    monkeypatch.setattr(manager, "cmd_maintain", _failing_maintain, raising=False)
    monkeypatch.setattr(sys, "argv", ["manager.py", "maintain", "--scheduled"])

    exit_code = manager.main()

    mirror_dir = desktop_dir / "Hermes-ZH-Failures" / "latest"
    assert exit_code == 1
    assert (bundle_dir / "failure-report.json").exists()
    assert (bundle_dir / "failure-report.md").exists()
    assert (mirror_dir / "failure-report.json").exists()
    assert (mirror_dir / "failure-report.md").exists()

    report = json.loads((bundle_dir / "failure-report.json").read_text(encoding="utf-8"))
    assert report["command"] == "maintain"
    assert report["error"] == "synthetic maintain failure"
    assert report["head"] == "deadbee"
    assert report["supported_commit"] == "abc123"


def test_payload_manager_recovers_accidental_update_with_overlay_present(tmp_path, monkeypatch):
    manager = _load_manager_module()
    patch_file = tmp_path / "hermes-zh-overlay.patch"
    patch_file.write_text("STALE\n", encoding="utf-8")
    calls = []

    monkeypatch.setattr(manager, "PATCH_FILE", patch_file, raising=False)
    monkeypatch.setattr(manager, "_ensure_dirs", lambda: None, raising=False)
    monkeypatch.setattr(
        manager,
        "_load_support_policy",
        lambda: {
            "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
            "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
            "maintenance_interval_seconds": 21600,
        },
        raising=False,
    )
    monkeypatch.setattr(manager, "_assert_supported_origin", lambda policy: None, raising=False)
    monkeypatch.setattr(manager, "_git_status", lambda: {"hermes_cli/main.py": " M"}, raising=False)
    monkeypatch.setattr(manager, "_unexpected_paths", lambda status_map: [], raising=False)
    monkeypatch.setattr(manager, "_unstage_managed_paths", lambda status_map: None, raising=False)
    monkeypatch.setattr(manager, "_overlay_present", lambda status_map: True, raising=False)
    monkeypatch.setattr(manager, "_fetch_upstream", lambda remote: None, raising=False)
    monkeypatch.setattr(manager, "_commit_exists", lambda ref: True, raising=False)
    monkeypatch.setattr(manager, "_pending_commits", lambda ref: 0, raising=False)
    monkeypatch.setattr(
        manager,
        "_generate_patch_text_for_ref",
        lambda ref: calls.append(("build_patch", ref)) or "NEW PATCH\n",
        raising=False,
    )
    monkeypatch.setattr(manager, "_hard_reset_to_ref", lambda ref: calls.append(("reset", ref)), raising=False)
    monkeypatch.setattr(manager, "_apply_patch", lambda reverse=False: calls.append(("apply_patch", reverse)), raising=False)
    monkeypatch.setattr(manager, "_reinstall", lambda: calls.append(("reinstall", None)), raising=False)
    monkeypatch.setattr(
        manager,
        "_run_scan",
        lambda: {
            "summary": {
                "ui_total": 1353,
                "commands_total": 52,
                "skills_total": 93,
                "skins_total": 80,
                "source_control_violations": 0,
                "source_control_new_files": 0,
            },
            "missing": {},
            "new_since_baseline": {},
        },
        raising=False,
    )
    monkeypatch.setattr(manager, "_refresh_baseline", lambda: calls.append(("refresh_baseline", None)), raising=False)
    monkeypatch.setattr(manager, "_sync_launchd_schedule_from_policy", lambda: calls.append(("sync_launchd", None)), raising=False)
    monkeypatch.setattr(manager, "_head_short", lambda: "01906e99", raising=False)

    class _Completed:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append(tuple(cmd))
        if cmd == ["git", "rev-parse", "HEAD"]:
            return _Completed("deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\n")
        return _Completed("")

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    exit_code = manager.cmd_maintain(type("Args", (), {"scheduled": False})())

    assert exit_code == 0
    assert ("build_patch", "01906e99dd225b7946c770479fcd9cc2949e7104") in calls
    assert ("reset", "01906e99dd225b7946c770479fcd9cc2949e7104") in calls
    assert ("apply_patch", False) in calls
    assert ("reinstall", None) in calls
    assert patch_file.read_text(encoding="utf-8") == "NEW PATCH\n"


def test_payload_manager_syncs_published_release_truth_into_active_files(tmp_path, monkeypatch):
    manager = _load_manager_module()
    release_repo = tmp_path / "hermes-zh-overlay-release"
    release_policy = release_repo / "payload" / "localization" / "support-policy.json"
    release_manager = release_repo / "payload" / "scripts" / "hermes_zh_overlay_manager.py"
    active_policy = tmp_path / "localization" / "support-policy.json"
    active_manager = tmp_path / "scripts" / "hermes_zh_overlay_manager.py"

    release_policy.parent.mkdir(parents=True, exist_ok=True)
    release_manager.parent.mkdir(parents=True, exist_ok=True)
    active_policy.parent.mkdir(parents=True, exist_ok=True)
    active_manager.parent.mkdir(parents=True, exist_ok=True)

    release_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "6ea7386a6f010320c8744cee6a1ac7835bc37ffc",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    release_manager.write_text("# release manager\n", encoding="utf-8")
    active_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    active_manager.write_text("# stale manager\n", encoding="utf-8")

    monkeypatch.setattr(manager, "RELEASE_REPO_DIR", release_repo, raising=False)
    monkeypatch.setattr(manager, "SUPPORT_POLICY_FILE", active_policy, raising=False)
    monkeypatch.setattr(manager, "LOCAL_MANAGER_FILE", active_manager, raising=False)

    calls = []

    class _Completed:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append((tuple(cmd), Path(cwd) if cwd is not None else None))
        if cmd == ["git", "show", "origin/main:payload/localization/support-policy.json"]:
            return _Completed(
                json.dumps(
                    {
                        "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                        "supported_commit": "6ea7386a6f010320c8744cee6a1ac7835bc37ffc",
                        "maintenance_interval_seconds": 21600,
                        "tolerated_unexpected_files": ["web/package-lock.json"],
                    }
                )
                + "\n"
            )
        if cmd == ["git", "show", "origin/main:payload/scripts/hermes_zh_overlay_manager.py"]:
            return _Completed("# release manager\n")
        if cmd == ["git", "status", "--porcelain", "--untracked-files=all"]:
            return _Completed("")
        if cmd == ["git", "rev-list", "HEAD..origin/main", "--count"]:
            return _Completed("1\n")
        return _Completed("")

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    result = manager._sync_published_release_truth()

    assert result == {
        "release_repo_used": True,
        "release_repo_updated": True,
        "support_policy_updated": True,
        "manager_script_updated": True,
    }
    assert json.loads(active_policy.read_text(encoding="utf-8"))["supported_commit"] == (
        "6ea7386a6f010320c8744cee6a1ac7835bc37ffc"
    )
    assert active_manager.read_text(encoding="utf-8") == "# release manager\n"
    assert ((("git", "fetch", "origin"), release_repo)) in calls
    assert ((("git", "merge", "--ff-only", "origin/main"), release_repo)) in calls


def test_payload_manager_syncs_remote_support_policy_even_when_release_repo_is_dirty(tmp_path, monkeypatch):
    manager = _load_manager_module()
    release_repo = tmp_path / "hermes-zh-overlay-release"
    release_policy = release_repo / "payload" / "localization" / "support-policy.json"
    release_manager = release_repo / "payload" / "scripts" / "hermes_zh_overlay_manager.py"
    active_policy = tmp_path / "localization" / "support-policy.json"
    active_manager = tmp_path / "scripts" / "hermes_zh_overlay_manager.py"

    release_policy.parent.mkdir(parents=True, exist_ok=True)
    release_manager.parent.mkdir(parents=True, exist_ok=True)
    active_policy.parent.mkdir(parents=True, exist_ok=True)
    active_manager.parent.mkdir(parents=True, exist_ok=True)

    release_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    release_manager.write_text("# local working-tree manager\n", encoding="utf-8")
    active_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    active_manager.write_text("# stale manager\n", encoding="utf-8")

    monkeypatch.setattr(manager, "RELEASE_REPO_DIR", release_repo, raising=False)
    monkeypatch.setattr(manager, "SUPPORT_POLICY_FILE", active_policy, raising=False)
    monkeypatch.setattr(manager, "LOCAL_MANAGER_FILE", active_manager, raising=False)

    calls = []

    class _Completed:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append((tuple(cmd), Path(cwd) if cwd is not None else None))
        if cmd == ["git", "show", "origin/main:payload/localization/support-policy.json"]:
            return _Completed(
                json.dumps(
                    {
                        "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                        "supported_commit": "6ea7386a6f010320c8744cee6a1ac7835bc37ffc",
                        "maintenance_interval_seconds": 21600,
                        "tolerated_unexpected_files": ["web/package-lock.json"],
                    }
                )
                + "\n"
            )
        if cmd == ["git", "show", "origin/main:payload/scripts/hermes_zh_overlay_manager.py"]:
            return _Completed("# published manager\n")
        if cmd == ["git", "status", "--porcelain", "--untracked-files=all"]:
            return _Completed(" M payload/scripts/hermes_zh_overlay_manager.py\n")
        if cmd == ["git", "rev-list", "HEAD..origin/main", "--count"]:
            return _Completed("1\n")
        return _Completed("")

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    result = manager._sync_published_release_truth()

    assert result == {
        "release_repo_used": True,
        "release_repo_updated": False,
        "support_policy_updated": True,
        "manager_script_updated": True,
    }
    assert json.loads(active_policy.read_text(encoding="utf-8"))["supported_commit"] == (
        "6ea7386a6f010320c8744cee6a1ac7835bc37ffc"
    )
    assert active_manager.read_text(encoding="utf-8") == "# published manager\n"
    assert ((("git", "fetch", "origin"), release_repo)) in calls
    assert ((("git", "merge", "--ff-only", "origin/main"), release_repo)) not in calls


def test_payload_manager_uses_cached_origin_support_policy_when_fetch_fails(tmp_path, monkeypatch):
    manager = _load_manager_module()
    release_repo = tmp_path / "hermes-zh-overlay-release"
    release_policy = release_repo / "payload" / "localization" / "support-policy.json"
    release_manager = release_repo / "payload" / "scripts" / "hermes_zh_overlay_manager.py"
    active_policy = tmp_path / "localization" / "support-policy.json"
    active_manager = tmp_path / "scripts" / "hermes_zh_overlay_manager.py"

    release_policy.parent.mkdir(parents=True, exist_ok=True)
    release_manager.parent.mkdir(parents=True, exist_ok=True)
    active_policy.parent.mkdir(parents=True, exist_ok=True)
    active_manager.parent.mkdir(parents=True, exist_ok=True)

    release_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    release_manager.write_text("# local working-tree manager\n", encoding="utf-8")
    active_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    active_manager.write_text("# stale manager\n", encoding="utf-8")

    monkeypatch.setattr(manager, "RELEASE_REPO_DIR", release_repo, raising=False)
    monkeypatch.setattr(manager, "SUPPORT_POLICY_FILE", active_policy, raising=False)
    monkeypatch.setattr(manager, "LOCAL_MANAGER_FILE", active_manager, raising=False)

    calls = []

    class _Completed:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append((tuple(cmd), Path(cwd) if cwd is not None else None))
        if cmd == ["git", "fetch", "origin"]:
            raise manager.OverlayError("git fetch origin failed: network")
        if cmd == ["git", "show", "origin/main:payload/localization/support-policy.json"]:
            return _Completed(
                json.dumps(
                    {
                        "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                        "supported_commit": "6ea7386a6f010320c8744cee6a1ac7835bc37ffc",
                        "maintenance_interval_seconds": 21600,
                        "tolerated_unexpected_files": ["web/package-lock.json"],
                    }
                )
                + "\n"
            )
        if cmd == ["git", "show", "origin/main:payload/scripts/hermes_zh_overlay_manager.py"]:
            return _Completed("# published manager from cached origin\n")
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    result = manager._sync_published_release_truth()

    assert result == {
        "release_repo_used": True,
        "release_repo_updated": False,
        "support_policy_updated": True,
        "manager_script_updated": True,
    }
    assert json.loads(active_policy.read_text(encoding="utf-8"))["supported_commit"] == (
        "6ea7386a6f010320c8744cee6a1ac7835bc37ffc"
    )
    assert active_manager.read_text(encoding="utf-8") == "# published manager from cached origin\n"
    assert ((("git", "fetch", "origin"), release_repo)) in calls
    assert ((("git", "show", "origin/main:payload/localization/support-policy.json"), release_repo)) in calls
    assert ((("git", "show", "origin/main:payload/scripts/hermes_zh_overlay_manager.py"), release_repo)) in calls


def test_payload_manager_keeps_active_policy_when_remote_policy_is_invalid(tmp_path, monkeypatch):
    manager = _load_manager_module()
    release_repo = tmp_path / "hermes-zh-overlay-release"
    release_policy = release_repo / "payload" / "localization" / "support-policy.json"
    release_manager = release_repo / "payload" / "scripts" / "hermes_zh_overlay_manager.py"
    active_policy = tmp_path / "localization" / "support-policy.json"
    active_manager = tmp_path / "scripts" / "hermes_zh_overlay_manager.py"

    release_policy.parent.mkdir(parents=True, exist_ok=True)
    release_manager.parent.mkdir(parents=True, exist_ok=True)
    active_policy.parent.mkdir(parents=True, exist_ok=True)
    active_manager.parent.mkdir(parents=True, exist_ok=True)

    release_policy.write_text("", encoding="utf-8")
    release_manager.write_text("# stale manager\n", encoding="utf-8")
    active_policy.write_text(
        json.dumps(
            {
                "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
                "supported_commit": "01906e99dd225b7946c770479fcd9cc2949e7104",
                "maintenance_interval_seconds": 21600,
                "tolerated_unexpected_files": ["web/package-lock.json"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    active_manager.write_text("# stale manager\n", encoding="utf-8")

    monkeypatch.setattr(manager, "RELEASE_REPO_DIR", release_repo, raising=False)
    monkeypatch.setattr(manager, "SUPPORT_POLICY_FILE", active_policy, raising=False)
    monkeypatch.setattr(manager, "LOCAL_MANAGER_FILE", active_manager, raising=False)

    calls = []

    class _Completed:
        def __init__(self, stdout=""):
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0

    def _fake_run(cmd, *, cwd=None, ok_codes=(0,)):
        calls.append((tuple(cmd), Path(cwd) if cwd is not None else None))
        if cmd == ["git", "show", "origin/main:payload/localization/support-policy.json"]:
            return _Completed("")
        if cmd == ["git", "show", "origin/main:payload/scripts/hermes_zh_overlay_manager.py"]:
            return _Completed("# stale manager\n")
        if cmd == ["git", "status", "--porcelain", "--untracked-files=all"]:
            return _Completed(" M payload/scripts/hermes_zh_overlay_manager.py\n")
        return _Completed("")

    monkeypatch.setattr(manager, "_run", _fake_run, raising=False)

    result = manager._sync_published_release_truth()

    assert result == {
        "release_repo_used": True,
        "release_repo_updated": False,
        "support_policy_updated": False,
        "manager_script_updated": False,
    }
    assert json.loads(active_policy.read_text(encoding="utf-8"))["supported_commit"] == (
        "01906e99dd225b7946c770479fcd9cc2949e7104"
    )
    assert active_manager.read_text(encoding="utf-8") == "# stale manager\n"
