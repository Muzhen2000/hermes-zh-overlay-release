#!/usr/bin/env python3
"""Install the Hermes Chinese overlay release payload on macOS."""

from __future__ import annotations

import argparse
import json
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/Muzhen2000/hermes-zh-overlay-release.git"
LAUNCHD_LABEL = "com.muzhen.hermes-zh-overlay-maintain"


class InstallError(RuntimeError):
    """Installer failure."""


def _run(cmd: list[str], *, cwd: Path | None = None, ok_codes: tuple[int, ...] = (0,)) -> None:
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    if result.returncode not in ok_codes:
        details = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
        raise InstallError(f"{' '.join(cmd)} failed: {details}")


def _write_bytes_if_changed(data: bytes, destination: Path) -> bool:
    if destination.exists() and destination.read_bytes() == data:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(destination.name + ".tmp")
    temp_path.write_bytes(data)
    temp_path.replace(destination)
    return True


def _clone_or_update_release_repo(
    *,
    release_dir: Path,
    repo_url: str,
    source_dir: Path | None,
) -> Path:
    if source_dir is not None:
        source_dir = source_dir.expanduser().resolve()
        if release_dir.resolve() == source_dir:
            return release_dir
        if release_dir.exists():
            shutil.rmtree(release_dir)
        _run(["git", "clone", str(source_dir), str(release_dir)])
        return release_dir

    if release_dir.exists():
        if not (release_dir / ".git").exists():
            raise InstallError(f"release directory exists but is not a git checkout: {release_dir}")
        _run(["git", "fetch", "origin"], cwd=release_dir)
        _run(["git", "merge", "--ff-only", "origin/main"], cwd=release_dir)
        return release_dir

    release_dir.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", repo_url, str(release_dir)])
    return release_dir


def _install_payload(*, release_dir: Path, hermes_home: Path) -> dict[str, bool]:
    support_policy = release_dir / "payload" / "localization" / "support-policy.json"
    manager = release_dir / "payload" / "scripts" / "hermes_zh_overlay_manager.py"
    if not support_policy.exists() or not manager.exists():
        raise InstallError(f"release payload is incomplete: {release_dir}")

    json.loads(support_policy.read_text(encoding="utf-8"))
    return {
        "support_policy": _write_bytes_if_changed(
            support_policy.read_bytes(),
            hermes_home / "localization" / "support-policy.json",
        ),
        "manager": _write_bytes_if_changed(
            manager.read_bytes(),
            hermes_home / "scripts" / "hermes_zh_overlay_manager.py",
        ),
    }


def _write_launchd_plist(*, hermes_home: Path, user_home: Path, python: str) -> Path:
    policy_path = hermes_home / "localization" / "support-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    interval = int(policy.get("maintenance_interval_seconds", 21600) or 21600)
    plist_path = user_home / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    payload = {
        "Label": LAUNCHD_LABEL,
        "ProgramArguments": [
            python,
            str(hermes_home / "scripts" / "hermes_zh_overlay_manager.py"),
            "maintain",
            "--scheduled",
        ],
        "WorkingDirectory": str(hermes_home),
        "RunAtLoad": True,
        "StartInterval": interval,
        "StandardOutPath": str(hermes_home / "logs" / "hermes-zh-overlay-maintain.log"),
        "StandardErrorPath": str(hermes_home / "logs" / "hermes-zh-overlay-maintain.err.log"),
        "EnvironmentVariables": {"HERMES_HOME": str(hermes_home)},
    }
    _write_bytes_if_changed(plistlib.dumps(payload), plist_path)
    return plist_path


def _bootstrap_launchd(plist_path: Path) -> None:
    domain = f"gui/{subprocess.check_output(['id', '-u'], text=True).strip()}"
    target = f"{domain}/{LAUNCHD_LABEL}"
    _run(["launchctl", "bootout", target], ok_codes=(0, 3, 36, 113))
    _run(["launchctl", "bootstrap", domain, str(plist_path)])


def install(
    *,
    hermes_home: Path,
    user_home: Path,
    repo_url: str = DEFAULT_REPO_URL,
    source_dir: Path | None = None,
    bootstrap: bool = True,
    run_maintain: bool = True,
) -> dict:
    hermes_home = hermes_home.expanduser()
    user_home = user_home.expanduser()
    release_dir = hermes_home / "hermes-zh-overlay-release"
    release_dir = _clone_or_update_release_repo(
        release_dir=release_dir,
        repo_url=repo_url,
        source_dir=source_dir,
    )
    changed = _install_payload(release_dir=release_dir, hermes_home=hermes_home)
    hermes_home.joinpath("logs").mkdir(parents=True, exist_ok=True)
    python = shutil.which("python3") or sys.executable
    plist_path = _write_launchd_plist(hermes_home=hermes_home, user_home=user_home, python=python)

    if bootstrap:
        _bootstrap_launchd(plist_path)
    if run_maintain:
        _run([python, str(hermes_home / "scripts" / "hermes_zh_overlay_manager.py"), "maintain"])

    return {
        "release_dir": str(release_dir),
        "support_policy_changed": changed["support_policy"],
        "manager_changed": changed["manager"],
        "launchd_plist": str(plist_path),
        "bootstrap": bootstrap,
        "run_maintain": run_maintain,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hermes-home", default=str(Path.home() / ".hermes"))
    parser.add_argument("--home", default=str(Path.home()))
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--source-dir", default="")
    parser.add_argument("--no-bootstrap", action="store_true")
    parser.add_argument("--no-maintain", action="store_true")
    args = parser.parse_args()

    try:
        result = install(
            hermes_home=Path(args.hermes_home),
            user_home=Path(args.home),
            repo_url=args.repo_url,
            source_dir=Path(args.source_dir) if args.source_dir else None,
            bootstrap=not args.no_bootstrap,
            run_maintain=not args.no_maintain,
        )
    except InstallError as exc:
        print(f"[hermes-zh-overlay-install] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
