"""Minimal failure bundle generation for unattended release Task 5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from payload.scripts.hermes_zh_overlay_manager import mirror_failure_bundle

ROOT = Path(__file__).resolve().parents[1]


def build_failure_bundle(bundle_dir: Path, *, desktop_dir: Path) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)

    (bundle_dir / "failure-report.json").write_text(
        json.dumps({"failure_stage": "scan"}) + "\n",
        encoding="utf-8",
    )
    (bundle_dir / "failure-report.md").write_text("# Failure Report\n", encoding="utf-8")

    mirror_failure_bundle(bundle_dir, desktop_root=desktop_dir)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bundle-dir",
        default=str(ROOT / "out" / "failure-bundle"),
        help="Path to write the generated failure bundle.",
    )
    parser.add_argument(
        "--desktop-dir",
        default=str(Path.home() / "Desktop"),
        help="Desktop directory used for local mirror output.",
    )
    args = parser.parse_args()

    build_failure_bundle(
        Path(args.bundle_dir),
        desktop_dir=Path(args.desktop_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
