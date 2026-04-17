#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/Muzhen2000/hermes-zh-overlay-release.git"
LEGACY_LAUNCHD_LABEL = "com.muzhen.hermes-zh-overlay-maintain"


class ReleaseError(RuntimeError):
    """Raised when a release apply step fails."""


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    ok_codes: tuple[int, ...] = (0,),
    capture_output: bool = True,
) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=capture_output,
        text=True,
    )
    if result.returncode not in ok_codes:
        details = (result.stderr or result.stdout or f"exit {result.returncode}").strip()
        raise ReleaseError(f"{' '.join(cmd)} failed: {details}")
    return (result.stdout or "").strip()


def _write_bytes_if_changed(data: bytes, destination: Path) -> bool:
    if destination.exists() and destination.read_bytes() == data:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(destination.name + ".tmp")
    temp_path.write_bytes(data)
    temp_path.replace(destination)
    return True


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReleaseError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"invalid json: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ReleaseError(f"expected object json: {path}")
    return data


def _clone_or_update_release_repo(
    *,
    release_dir: Path,
    repo_url: str,
    source_dir: Path | None,
) -> Path:
    if source_dir is not None:
        source_dir = source_dir.expanduser().resolve()
        if not (source_dir / ".git").exists():
            raise ReleaseError(f"release source dir is not a git checkout: {source_dir}")
        if release_dir.resolve() == source_dir:
            return release_dir
        if release_dir.exists():
            shutil.rmtree(release_dir)
        _run(["git", "clone", str(source_dir), str(release_dir)])
        return release_dir

    if release_dir.exists():
        if not (release_dir / ".git").exists():
            raise ReleaseError(f"release dir exists but is not a git checkout: {release_dir}")
        _run(["git", "fetch", "origin"], cwd=release_dir)
        _run(["git", "merge", "--ff-only", "origin/main"], cwd=release_dir)
        return release_dir

    release_dir.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", repo_url, str(release_dir)])
    return release_dir


def _load_release_metadata(repo_root: Path, release_id: str | None = None) -> tuple[str, dict, dict]:
    release_index = _read_json(repo_root / "release.json")
    resolved_release = release_id or str(release_index.get("latest_release") or "").strip()
    if not resolved_release:
        raise ReleaseError("release.json does not define latest_release")
    manifest = _read_json(repo_root / "releases" / resolved_release / "manifest.json")
    return resolved_release, release_index, manifest


def _copy_release_assets(*, repo_root: Path, hermes_home: Path, release_id: str, manifest: dict) -> dict:
    release_dir = repo_root / "releases" / release_id
    localization_dir = hermes_home / "localization"
    patch_dir = localization_dir / "patches"
    changed: dict[str, bool] = {}

    for name in manifest.get("localization_files", []):
        source = release_dir / "localization" / name
        if not source.exists():
            raise ReleaseError(f"missing localization asset: {source}")
        destination = localization_dir / name
        changed[name] = _write_bytes_if_changed(source.read_bytes(), destination)

    patch_rel = str(manifest.get("patch") or "").strip()
    if not patch_rel:
        raise ReleaseError("manifest does not define patch")
    patch_source = release_dir / patch_rel
    if not patch_source.exists():
        raise ReleaseError(f"missing patch asset: {patch_source}")
    patch_destination = patch_dir / f"hermes-zh-{release_id}.patch"
    changed[patch_destination.name] = _write_bytes_if_changed(
        patch_source.read_bytes(),
        patch_destination,
    )
    return {"changed": changed, "patch_path": str(patch_destination)}


def _remove_path(path: Path) -> bool:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
        return True
    if path.is_dir():
        shutil.rmtree(path)
        return True
    return False


def _prune_legacy_overlay(hermes_home: Path, user_home: Path) -> list[str]:
    removed: list[str] = []
    plist_path = user_home / "Library" / "LaunchAgents" / f"{LEGACY_LAUNCHD_LABEL}.plist"
    launchctl = shutil.which("launchctl")
    if plist_path.exists() and launchctl:
        domain = f"gui/{_run(['id', '-u'])}"
        target = f"{domain}/{LEGACY_LAUNCHD_LABEL}"
        try:
            _run([launchctl, "bootout", target], ok_codes=(0, 3, 36, 113))
        except ReleaseError:
            pass
    for path in [
        plist_path,
        hermes_home / "scripts" / "hermes_zh_overlay_manager.py",
        hermes_home / "localization" / "support-policy.json",
        hermes_home / "localization" / "reports",
        hermes_home / "localization" / "patches" / "hermes-zh-overlay.patch",
    ]:
        if _remove_path(path):
            removed.append(str(path))
    return removed


def _align_source_to_official(*, source_dir: Path, official_repo: str, official_commit: str) -> None:
    if source_dir.exists() and not (source_dir / ".git").exists():
        raise ReleaseError(f"Hermes source dir exists but is not a git checkout: {source_dir}")
    if not source_dir.exists():
        source_dir.parent.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", official_repo, str(source_dir)])
    _run(["git", "fetch", official_repo, official_commit], cwd=source_dir)
    _run(["git", "checkout", "--force", "--detach", official_commit], cwd=source_dir)
    _run(["git", "clean", "-fd"], cwd=source_dir)


def _apply_patch(*, source_dir: Path, patch_path: Path) -> None:
    _run(["git", "apply", "--check", str(patch_path)], cwd=source_dir)
    _run(["git", "apply", str(patch_path)], cwd=source_dir)


def apply_release(
    *,
    hermes_home: Path,
    repo_url: str = DEFAULT_REPO_URL,
    release_id: str | None = None,
    release_source_dir: Path | None = None,
) -> dict:
    hermes_home = hermes_home.expanduser()
    user_home = Path.home()
    release_checkout = hermes_home / "hermes-zh-overlay-release"
    repo_root = _clone_or_update_release_repo(
        release_dir=release_checkout,
        repo_url=repo_url,
        source_dir=release_source_dir,
    )
    resolved_release, release_index, manifest = _load_release_metadata(repo_root, release_id)
    official_repo = str(release_index.get("official_repo") or "").strip()
    if not official_repo:
        raise ReleaseError("release.json does not define official_repo")
    official_commit = str(manifest.get("official_commit") or "").strip()
    if not official_commit:
        raise ReleaseError("manifest does not define official_commit")

    copied = _copy_release_assets(
        repo_root=repo_root,
        hermes_home=hermes_home,
        release_id=resolved_release,
        manifest=manifest,
    )
    removed = _prune_legacy_overlay(hermes_home, user_home)

    source_dir = hermes_home / "hermes-agent"
    _align_source_to_official(
        source_dir=source_dir,
        official_repo=official_repo,
        official_commit=official_commit,
    )
    _apply_patch(source_dir=source_dir, patch_path=Path(copied["patch_path"]))

    return {
        "release": resolved_release,
        "official_commit": official_commit,
        "official_repo": official_repo,
        "repo_root": str(repo_root),
        "source_dir": str(source_dir),
        "patch_path": copied["patch_path"],
        "localization_changed": copied["changed"],
        "legacy_removed": removed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a versioned Hermes Chinese release.")
    parser.add_argument("--hermes-home", default=str(Path.home() / ".hermes"))
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--release", default="")
    parser.add_argument("--release-source-dir", default="")
    args = parser.parse_args()

    try:
        result = apply_release(
            hermes_home=Path(args.hermes_home),
            repo_url=args.repo_url,
            release_id=args.release or None,
            release_source_dir=Path(args.release_source_dir) if args.release_source_dir else None,
        )
    except ReleaseError as exc:
        print(f"[hermes-zh-release] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
