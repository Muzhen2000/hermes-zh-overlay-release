"""Minimal candidate gate for unattended release Task 3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_candidate(*, scan_summary: dict, tests_ok: bool, overlay_ok: bool) -> dict:
    if not overlay_ok:
        return {"publishable": False, "failure_stage": "overlay"}
    if scan_summary.get("missing", 0) != 0 or scan_summary.get("control", 0) != 0:
        return {"publishable": False, "failure_stage": "scan"}
    if not tests_ok:
        return {"publishable": False, "failure_stage": "tests"}
    return {"publishable": True, "failure_stage": None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay-ok", action="store_true")
    parser.add_argument("--tests-ok", action="store_true")
    parser.add_argument("--scan-missing", type=int, default=0)
    parser.add_argument("--scan-control", type=int, default=0)
    args = parser.parse_args()

    result = validate_candidate(
        scan_summary={"missing": args.scan_missing, "control": args.scan_control},
        tests_ok=args.tests_ok,
        overlay_ok=args.overlay_ok,
    )
    out_dir = ROOT / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "validation.json").write_text(json.dumps(result), encoding="utf-8")
    if not result["publishable"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
