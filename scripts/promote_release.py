"""Promote a validated upstream candidate into the release truth."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def promote_release(
    upstream_state: dict,
    release_path: Path,
    support_policy_path: Path,
) -> dict:
    release_payload = json.loads(release_path.read_text(encoding="utf-8"))
    support_policy = json.loads(support_policy_path.read_text(encoding="utf-8"))

    current_supported_commit = release_payload["supported_commit"]
    candidate_commit = upstream_state["official_latest"]
    should_promote = bool(upstream_state.get("needs_release")) and candidate_commit != current_supported_commit

    if should_promote:
        release_payload["supported_commit"] = candidate_commit
        support_policy["supported_commit"] = candidate_commit
        release_path.write_text(
            json.dumps(release_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        support_policy_path.write_text(
            json.dumps(support_policy, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return {
        "promoted": should_promote,
        "from_commit": current_supported_commit,
        "to_commit": candidate_commit if should_promote else current_supported_commit,
    }


def main() -> int:
    upstream_state = json.loads((ROOT / "out" / "upstream.json").read_text(encoding="utf-8"))
    result = promote_release(
        upstream_state,
        ROOT / "release.json",
        ROOT / "payload" / "localization" / "support-policy.json",
    )
    out_dir = ROOT / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "promotion.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
