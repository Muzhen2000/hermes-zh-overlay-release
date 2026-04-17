"""Minimal upstream comparison for unattended release Task 2."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fetch_official_latest(official_repo: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", official_repo, "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    parts = result.stdout.split()
    if not parts:
        raise RuntimeError(f"git ls-remote returned no refs for {official_repo!r}")
    return parts[0]


def check_upstream(official_latest: str, supported_commit: str) -> dict:
    return {
        "official_latest": official_latest,
        "supported_commit": supported_commit,
        "needs_release": official_latest != supported_commit,
    }


def main() -> int:
    release = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
    latest = fetch_official_latest(release["official_repo"])
    state = check_upstream(official_latest=latest, supported_commit=release["supported_commit"])
    out_dir = ROOT / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "upstream.json").write_text(json.dumps(state), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
