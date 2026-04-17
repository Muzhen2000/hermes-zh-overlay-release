"""Minimal local helper for unattended release Task 6."""

from __future__ import annotations

import shutil
from pathlib import Path


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
