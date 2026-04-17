from __future__ import annotations

import importlib.util
from pathlib import Path


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
