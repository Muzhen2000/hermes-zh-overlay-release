#!/usr/bin/env python3
"""Deterministic manager for the Hermes Chinese localization overlay."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile

HERMES_HOME = Path.home() / ".hermes"
REPO_DIR = HERMES_HOME / "hermes-agent"
PATCH_FILE = HERMES_HOME / "localization" / "patches" / "hermes-zh-overlay.patch"
SUPPORT_POLICY_FILE = HERMES_HOME / "localization" / "support-policy.json"
SCAN_SCRIPT = HERMES_HOME / "scripts" / "scan_hermes_localization.py"
LATEST_SCAN_FILE = HERMES_HOME / "localization" / "reports" / "hermes-zh-scan-latest.json"
BASELINE_SCAN_FILE = HERMES_HOME / "localization" / "reports" / "hermes-zh-baseline.json"
LOG_DIR = HERMES_HOME / "logs"
LAUNCHD_LABEL = "com.muzhen.hermes-zh-overlay-maintain"
LAUNCHD_PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"

STATUS_IGNORE = {".DS_Store"}
MANAGED_REPO_FILES = (
    "agent/display.py",
    "agent/manual_compression_feedback.py",
    "cli.py",
    "gateway/run.py",
    "gateway/platforms/telegram.py",
    "hermes_cli/auth.py",
    "hermes_cli/banner.py",
    "hermes_cli/commands.py",
    "hermes_cli/debug.py",
    "hermes_cli/gateway.py",
    "hermes_cli/main.py",
    "hermes_cli/skin_engine.py",
    "hermes_cli/status.py",
    "hermes_cli/tips.py",
    "tools/skills_tool.py",
)
MANAGED_REPO_SET = set(MANAGED_REPO_FILES)
DEFAULT_SUPPORT_POLICY = {
    "upstream_repo": "https://github.com/NousResearch/hermes-agent.git",
    "supported_commit": "",
    "maintenance_interval_seconds": 21600,
    "tolerated_unexpected_files": [],
}


class OverlayError(RuntimeError):
    """Overlay manager failure."""


def decide_local_target(*, release_supported_commit: str, origin_main_commit: str) -> str:
    return release_supported_commit


def mirror_failure_bundle(bundle_dir: Path, *, desktop_root: Path) -> Path:
    target = desktop_root / "Hermes-ZH-Failures" / "latest"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    for item in bundle_dir.rglob("*"):
        if item.is_file():
            destination = target / item.relative_to(bundle_dir)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)

    return target


def _ensure_dirs() -> None:
    PATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _load_support_policy() -> dict:
    payload = dict(DEFAULT_SUPPORT_POLICY)
    if SUPPORT_POLICY_FILE.exists():
        try:
            data = json.loads(SUPPORT_POLICY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OverlayError(f"invalid support policy {SUPPORT_POLICY_FILE}: {exc}") from exc
        if not isinstance(data, dict):
            raise OverlayError(f"invalid support policy {SUPPORT_POLICY_FILE}: expected object")
        payload.update(data)
    tolerated = payload.get("tolerated_unexpected_files", [])
    if not isinstance(tolerated, list):
        tolerated = []
    payload["tolerated_unexpected_files"] = sorted({str(path).strip() for path in tolerated if str(path).strip()})
    payload["supported_commit"] = str(payload.get("supported_commit", "")).strip()
    payload["upstream_repo"] = str(payload.get("upstream_repo", DEFAULT_SUPPORT_POLICY["upstream_repo"])).strip()
    try:
        payload["maintenance_interval_seconds"] = int(payload.get("maintenance_interval_seconds", 21600) or 21600)
    except (TypeError, ValueError):
        payload["maintenance_interval_seconds"] = 21600
    return payload


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    ok_codes: tuple[int, ...] = (0,),
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd or REPO_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode not in ok_codes:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        details = stderr or stdout or f"exit {result.returncode}"
        raise OverlayError(f"{' '.join(cmd)} failed: {details}")
    return result


def _git_status() -> dict[str, str]:
    result = _run(["git", "status", "--porcelain", "--untracked-files=all"])
    items: dict[str, str] = {}
    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            items[path] = status
    return items


def _dirty_paths(status_map: dict[str, str]) -> set[str]:
    return {path for path in status_map if path not in STATUS_IGNORE}


def _unexpected_paths(status_map: dict[str, str]) -> list[str]:
    tolerated = set(_load_support_policy().get("tolerated_unexpected_files", []))
    return sorted(
        path
        for path in _dirty_paths(status_map)
        if path not in MANAGED_REPO_SET and path not in tolerated
    )


def _managed_dirty_paths(status_map: dict[str, str]) -> list[str]:
    return sorted(path for path in _dirty_paths(status_map) if path in MANAGED_REPO_SET)


def _unstage_managed_paths(status_map: dict[str, str]) -> None:
    paths = _managed_dirty_paths(status_map)
    if paths:
        _run(["git", "reset", "HEAD", "--", *paths])


def _overlay_present(status_map: dict[str, str]) -> bool:
    return bool(_managed_dirty_paths(status_map))


def _upstream_ref() -> str:
    try:
        return _run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
        ).stdout.strip()
    except OverlayError:
        return "origin/main"


def _normalize_remote_url(url: str) -> str:
    normalized = str(url or "").strip()
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.removeprefix("git@github.com:")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized.rstrip("/")


def _origin_url() -> str:
    return _run(["git", "remote", "get-url", "origin"]).stdout.strip()


def _assert_supported_origin(policy: dict) -> None:
    expected = _normalize_remote_url(policy.get("upstream_repo", ""))
    if not expected:
        return
    actual = _normalize_remote_url(_origin_url())
    if actual != expected:
        raise OverlayError(f"origin remote does not match support policy: {actual or 'unknown'} != {expected}")


def _launchd_domain() -> str:
    return f"gui/{os.getuid()}"


def _head_short() -> str:
    return _run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()


def _select_runtime_python() -> str:
    venv_python = REPO_DIR / "venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    python = shutil.which("python3")
    if python:
        return python
    raise OverlayError("python3 not found")


def _python_has_pip(python_exe: str) -> bool:
    result = subprocess.run(
        [python_exe, "-m", "pip", "--version"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _resolve_script_python(script_path: str) -> str | None:
    try:
        first_line = Path(script_path).read_text(encoding="utf-8").splitlines()[0].strip()
    except (OSError, UnicodeDecodeError, IndexError):
        return None

    if not first_line.startswith("#!"):
        return None

    shebang = first_line[2:].strip()
    if not shebang:
        return None

    if shebang.startswith("/usr/bin/env "):
        parts = shebang.split()
        if len(parts) >= 2:
            return shutil.which(parts[1])
        return None

    return shebang


def _candidate_install_pythons() -> list[str]:
    candidates: list[str] = []

    hermes_exe = shutil.which("hermes")
    if hermes_exe:
        launcher_python = _resolve_script_python(hermes_exe)
        if launcher_python:
            candidates.append(launcher_python)

    venv_python = REPO_DIR / "venv" / "bin" / "python"
    if venv_python.exists():
        candidates.append(str(venv_python))

    unique: list[str] = []
    seen: set[Path] = set()
    for candidate in candidates:
        expanded = Path(candidate).expanduser()
        try:
            resolved = expanded.resolve()
        except OSError:
            continue
        if not expanded.exists() or resolved in seen:
            continue
        seen.add(resolved)
        unique.append(str(expanded))

    return unique


def _reinstall() -> None:
    attempts: list[list[str]] = []
    uv = shutil.which("uv")
    for install_python in _candidate_install_pythons():
        if _python_has_pip(install_python):
            attempts.append([install_python, "-m", "pip", "install", "-e", "."])
        if uv:
            attempts.append(
                [uv, "pip", "install", "--python", install_python, "--editable", "."]
            )

    if not attempts:
        system_python = shutil.which("python3")
        if system_python and _python_has_pip(system_python):
            attempts.append([system_python, "-m", "pip", "install", "-e", "."])
        elif uv and system_python:
            attempts.append(
                [uv, "pip", "install", "--python", system_python, "--editable", "."]
            )

    errors: list[str] = []
    for cmd in attempts:
        try:
            _run(cmd)
            return
        except OverlayError as exc:
            errors.append(str(exc))

    if not errors:
        raise OverlayError("no usable reinstall command found")
    raise OverlayError("all reinstall commands failed: " + " | ".join(errors))


def _read_scan_payload() -> dict:
    if not LATEST_SCAN_FILE.exists():
        raise OverlayError(f"scan report not found: {LATEST_SCAN_FILE}")
    return json.loads(LATEST_SCAN_FILE.read_text(encoding="utf-8"))


def _scan_counts(payload: dict) -> tuple[int, int, int]:
    missing = payload.get("missing", {})
    new_since = payload.get("new_since_baseline", {})
    summary = payload.get("summary", {}) if isinstance(payload.get("summary"), dict) else {}

    def _count_mapping(mapping: dict) -> int:
        total = 0
        for value in mapping.values():
            if isinstance(value, list):
                total += len(value)
            else:
                total += int(value or 0)
        return total

    missing_total = _count_mapping(missing) if isinstance(missing, dict) else 0
    new_total = _count_mapping(new_since) if isinstance(new_since, dict) else 0
    control_total = int(summary.get("source_control_violations", 0) or 0)
    control_total += int(summary.get("source_control_new_files", 0) or 0)
    return missing_total + control_total, new_total, control_total


def _format_scan_summary(payload: dict) -> str:
    missing_total, new_total, control_total = _scan_counts(payload)
    summary = payload.get("summary", {}) if isinstance(payload.get("summary"), dict) else {}
    ui_total = summary.get("ui_total", "?")
    commands_total = summary.get("commands_total", "?")
    skills_total = summary.get("skills_total", "?")
    skins_total = summary.get("skins_total", "?")
    return (
        f"scan missing={missing_total} new_since_baseline={new_total} "
        f"(ui={ui_total}, commands={commands_total}, skills={skills_total}, skins={skins_total}, control={control_total})"
    )


def _run_scan() -> dict:
    if not SCAN_SCRIPT.exists():
        raise OverlayError(f"scan script not found: {SCAN_SCRIPT}")
    python = _select_runtime_python()
    _run([python, str(SCAN_SCRIPT)], cwd=HERMES_HOME)
    return _read_scan_payload()


def _refresh_baseline() -> None:
    if not LATEST_SCAN_FILE.exists():
        raise OverlayError(f"latest scan report not found: {LATEST_SCAN_FILE}")
    shutil.copy2(LATEST_SCAN_FILE, BASELINE_SCAN_FILE)


def _tracked_managed_paths(status_map: dict[str, str]) -> list[str]:
    return [
        path
        for path in MANAGED_REPO_FILES
        if path in status_map and status_map[path] != "??"
    ]


def _untracked_managed_paths(status_map: dict[str, str]) -> list[str]:
    return [
        path
        for path in MANAGED_REPO_FILES
        if path in status_map and status_map[path] == "??"
    ]


def _generate_patch_text() -> str:
    status_map = _git_status()
    unexpected = _unexpected_paths(status_map)
    if unexpected:
        raise OverlayError(
            "cannot refresh patch with unexpected repo changes: " + ", ".join(unexpected)
        )

    parts: list[str] = []
    tracked = _tracked_managed_paths(status_map)
    if tracked:
        parts.append(_run(["git", "diff", "--binary", "HEAD", "--", *tracked]).stdout)

    for rel_path in _untracked_managed_paths(status_map):
        result = subprocess.run(
            ["git", "diff", "--binary", "--no-index", "--", "/dev/null", rel_path],
            capture_output=True,
            text=True,
            cwd=str(REPO_DIR),
        )
        if result.returncode not in (0, 1):
            stderr = (result.stderr or "").strip()
            raise OverlayError(f"failed to diff untracked file {rel_path}: {stderr}")
        parts.append(result.stdout)

    normalized_parts: list[str] = []
    for part in parts:
        if not part:
            continue
        normalized_parts.append(part if part.endswith("\n") else part + "\n")
    patch_text = "".join(normalized_parts)
    if not patch_text.strip():
        raise OverlayError("no managed overlay diff found to write")
    return patch_text


def _generate_patch_text_for_ref(ref: str) -> str:
    status_map = _git_status()
    unexpected = _unexpected_paths(status_map)
    if unexpected:
        raise OverlayError(
            "cannot refresh patch for target ref with unexpected repo changes: "
            + ", ".join(unexpected)
        )

    tracked = _tracked_managed_paths(status_map)
    untracked = _untracked_managed_paths(status_map)
    if not tracked and not untracked:
        return ""

    tempdir = Path(tempfile.mkdtemp(prefix="hermes-zh-overlay-target-"))
    added = False
    try:
        _run(["git", "worktree", "add", "--detach", str(tempdir), ref], cwd=REPO_DIR)
        added = True
        for rel_path in tracked + untracked:
            source = REPO_DIR / rel_path
            destination = tempdir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        parts = [
            _run(["git", "diff", "--binary", "HEAD", "--", *(tracked + untracked)], cwd=tempdir).stdout
        ]
    finally:
        if added:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(tempdir)],
                cwd=str(REPO_DIR),
                capture_output=True,
                text=True,
            )
        shutil.rmtree(tempdir, ignore_errors=True)

    normalized_parts: list[str] = []
    for part in parts:
        if not part:
            continue
        normalized_parts.append(part if part.endswith("\n") else part + "\n")
    patch_text = "".join(normalized_parts)
    return patch_text


def _write_patch() -> int:
    _ensure_dirs()
    patch_text = _generate_patch_text()
    PATCH_FILE.write_text(patch_text, encoding="utf-8")
    status_map = _git_status()
    return len(_managed_dirty_paths(status_map))


def _patch_has_payload() -> bool:
    if not PATCH_FILE.exists():
        return False
    try:
        return bool(PATCH_FILE.read_text(encoding="utf-8").strip())
    except OSError as exc:
        raise OverlayError(f"failed to read overlay patch {PATCH_FILE}: {exc}") from exc


def _apply_patch(*, reverse: bool = False) -> str:
    if not PATCH_FILE.exists():
        raise OverlayError(f"overlay patch not found: {PATCH_FILE}")
    check_cmd = ["git", "apply"]
    apply_cmd = ["git", "apply", "--whitespace=nowarn"]
    if reverse:
        check_cmd.append("-R")
        apply_cmd.append("-R")
    check_cmd.extend(["--check", str(PATCH_FILE)])
    apply_cmd.append(str(PATCH_FILE))
    _run(check_cmd)
    _run(apply_cmd)
    return "removed" if reverse else "applied"


def _fetch_upstream(upstream: str) -> None:
    remote = upstream.split("/", 1)[0]
    _run(["git", "fetch", remote])


def _pending_commits(upstream: str) -> int:
    output = _run(["git", "rev-list", f"HEAD..{upstream}", "--count"]).stdout.strip()
    return int(output or "0")


def _ff_update(upstream: str) -> None:
    _run(["git", "merge", "--ff-only", upstream])


def _hard_reset_to_ref(ref: str) -> None:
    _run(["git", "reset", "--hard", ref])


def _sync_launchd_schedule_from_policy() -> bool:
    if not LAUNCHD_PLIST_PATH.exists():
        return False

    policy = _load_support_policy()
    desired_interval = int(policy.get("maintenance_interval_seconds", 21600) or 21600)
    try:
        payload = plistlib.loads(LAUNCHD_PLIST_PATH.read_bytes())
    except Exception as exc:
        raise OverlayError(f"invalid launchd plist {LAUNCHD_PLIST_PATH}: {exc}") from exc

    current_interval = payload.get("StartInterval")
    if current_interval == desired_interval:
        return False

    payload["StartInterval"] = desired_interval
    LAUNCHD_PLIST_PATH.write_bytes(plistlib.dumps(payload))
    target = f"{_launchd_domain()}/{LAUNCHD_LABEL}"
    _run(["launchctl", "bootout", target], cwd=HERMES_HOME, ok_codes=(0, 3, 36, 113))
    _run(["launchctl", "bootstrap", _launchd_domain(), str(LAUNCHD_PLIST_PATH)], cwd=HERMES_HOME)
    return True


def _commit_exists(ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=str(REPO_DIR),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _preflight_patch_on_ref(ref: str) -> None:
    tempdir = Path(tempfile.mkdtemp(prefix="hermes-zh-overlay-"))
    added = False
    try:
        _run(["git", "worktree", "add", "--detach", str(tempdir), ref], cwd=REPO_DIR)
        added = True
        _run(["git", "apply", "--check", str(PATCH_FILE)], cwd=tempdir)
    finally:
        if added:
            subprocess.run(
                ["git", "worktree", "remove", str(tempdir), "--force"],
                cwd=str(REPO_DIR),
                capture_output=True,
                text=True,
            )
        shutil.rmtree(tempdir, ignore_errors=True)


def cmd_status(_: argparse.Namespace) -> int:
    policy = _load_support_policy()
    status_map = _git_status()
    dirty = _managed_dirty_paths(status_map)
    unexpected = _unexpected_paths(status_map)
    print(f"head={_head_short()}")
    print(f"supported_commit={policy.get('supported_commit') or 'unset'}")
    print(f"maintenance_interval_seconds={policy.get('maintenance_interval_seconds', 21600)}")
    print(f"patch_file={PATCH_FILE}")
    print(f"patch_exists={'yes' if PATCH_FILE.exists() else 'no'}")
    print(f"overlay_present={'yes' if _overlay_present(status_map) else 'no'}")
    print(f"managed_dirty={len(dirty)}")
    if dirty:
        print("managed_files=" + ", ".join(dirty))
    print(f"unexpected_dirty={len(unexpected)}")
    if unexpected:
        print("unexpected_files=" + ", ".join(unexpected))
    if LATEST_SCAN_FILE.exists():
        payload = _read_scan_payload()
        print(_format_scan_summary(payload))
    else:
        print("scan_report=missing")
    return 0


def cmd_refresh_patch(_: argparse.Namespace) -> int:
    count = _write_patch()
    print(f"wrote overlay patch: {PATCH_FILE}")
    print(f"managed_files_in_diff={count}")
    return 0


def cmd_refresh_baseline(_: argparse.Namespace) -> int:
    _refresh_baseline()
    print(f"refreshed baseline: {BASELINE_SCAN_FILE}")
    return 0


def cmd_maintain(args: argparse.Namespace) -> int:
    _ensure_dirs()
    policy = _load_support_policy()
    _assert_supported_origin(policy)
    target_ref = policy.get("supported_commit", "")
    if not target_ref:
        raise OverlayError(f"supported_commit not set in {SUPPORT_POLICY_FILE}")
    status_map = _git_status()
    unexpected = _unexpected_paths(status_map)
    if unexpected:
        raise OverlayError(
            "unexpected repo changes outside overlay scope: " + ", ".join(unexpected)
        )

    _unstage_managed_paths(status_map)
    status_map = _git_status()
    overlay_present = _overlay_present(status_map)
    _fetch_upstream("origin")
    if not _commit_exists(target_ref):
        raise OverlayError(f"supported commit not available locally after fetch: {target_ref}")
    pending = _pending_commits(target_ref)
    current_head = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    recovered_to_supported = False

    if current_head != target_ref and pending == 0:
        if overlay_present:
            target_patch_text = _generate_patch_text_for_ref(target_ref)
            _hard_reset_to_ref(target_ref)
            PATCH_FILE.write_text(target_patch_text, encoding="utf-8")
            if target_patch_text.strip():
                _apply_patch()
            _reinstall()
            payload = _run_scan()
            missing_total, new_total, _ = _scan_counts(payload)
            if missing_total or new_total:
                raise OverlayError(
                    "recovered Hermes to supported commit, but localization scan found gaps: "
                    + _format_scan_summary(payload)
                )
            _refresh_baseline()
            print(f"recovered Hermes to supported commit {_head_short()}")
            print("overlay re-applied successfully")
            print(_format_scan_summary(payload))
            print(f"baseline_refreshed={BASELINE_SCAN_FILE}")
            _sync_launchd_schedule_from_policy()
            return 0
        _hard_reset_to_ref(target_ref)
        current_head = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
        recovered_to_supported = True

    if overlay_present and not _patch_has_payload():
        PATCH_FILE.write_text(_generate_patch_text(), encoding="utf-8")

    if pending == 0:
        if overlay_present:
            if args.scheduled:
                _sync_launchd_schedule_from_policy()
                return 0
            if not recovered_to_supported:
                print("already at supported Hermes commit; overlay already applied")
            else:
                print(f"recovered Hermes to supported commit {_head_short()}; overlay already applied")
            if LATEST_SCAN_FILE.exists():
                print(_format_scan_summary(_read_scan_payload()))
            _sync_launchd_schedule_from_policy()
            return 0

        _apply_patch()
        _reinstall()
        payload = _run_scan()
        missing_total, new_total, _ = _scan_counts(payload)
        if missing_total or new_total:
            raise OverlayError(
                "overlay applied, but localization scan found gaps: "
                + _format_scan_summary(payload)
            )
        _refresh_baseline()
        if not recovered_to_supported:
            print("overlay applied to a clean repo")
        else:
            print(f"recovered Hermes to supported commit {_head_short()}")
            print("overlay re-applied successfully")
        print(_format_scan_summary(payload))
        print(f"baseline_refreshed={BASELINE_SCAN_FILE}")
        _sync_launchd_schedule_from_policy()
        return 0

    target_patch_text = _generate_patch_text_for_ref(target_ref)

    _hard_reset_to_ref(target_ref)
    PATCH_FILE.write_text(target_patch_text, encoding="utf-8")
    if target_patch_text.strip():
        _apply_patch()
    _reinstall()
    payload = _run_scan()
    missing_total, new_total, _ = _scan_counts(payload)
    if missing_total or new_total:
        raise OverlayError(
            f"upstream updated by {pending} commit(s), but localization scan found gaps: "
            + _format_scan_summary(payload)
        )

    _refresh_baseline()
    print(f"updated Hermes to supported commit {_head_short()} (+{pending} commit(s))")
    print("overlay re-applied successfully")
    print(_format_scan_summary(payload))
    print(f"baseline_refreshed={BASELINE_SCAN_FILE}")
    _sync_launchd_schedule_from_policy()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show overlay manager status")
    status_parser.set_defaults(func=cmd_status)

    refresh_patch_parser = subparsers.add_parser(
        "refresh-patch", help="Write the external overlay patch from the current repo diff"
    )
    refresh_patch_parser.set_defaults(func=cmd_refresh_patch)

    refresh_baseline_parser = subparsers.add_parser(
        "refresh-baseline", help="Copy the latest clean scan report into the baseline file"
    )
    refresh_baseline_parser.set_defaults(func=cmd_refresh_baseline)

    maintain_parser = subparsers.add_parser(
        "maintain",
        help="Maintain the overlay: fetch upstream, update Hermes, re-apply patch, reinstall, and scan",
    )
    maintain_parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Suppress no-op output for scheduled runs",
    )
    maintain_parser.set_defaults(func=cmd_maintain)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except OverlayError as exc:
        print(f"[hermes-zh-overlay] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
