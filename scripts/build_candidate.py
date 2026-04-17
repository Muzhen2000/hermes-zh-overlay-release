"""Minimal candidate worktree bootstrap for unattended release Task 2."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]



def build_candidate(state: dict, candidate_dir: Path) -> dict:
    candidate_dir.mkdir(parents=True, exist_ok=True)
    return {
        "needs_release": state["needs_release"],
        "candidate_commit": state["official_latest"],
        "candidate_dir": str(candidate_dir),
    }


def main() -> int:
    state = json.loads((ROOT / "out" / "upstream.json").read_text(encoding="utf-8"))
    candidate_dir = ROOT / "out" / "candidate"
    result = build_candidate(state, candidate_dir)
    (ROOT / "out" / "candidate.json").write_text(json.dumps(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
