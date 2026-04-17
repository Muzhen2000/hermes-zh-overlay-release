from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_index_scope_is_terminal_and_telegram_only():
    release_index = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))

    assert release_index["scope"] == ["terminal", "telegram"]
    assert release_index["web_ui_policy"] == "upstream-only"


def test_manifest_lists_existing_localization_files():
    manifest = json.loads(
        (ROOT / "releases" / "31e72764" / "manifest.json").read_text(encoding="utf-8")
    )
    release_dir = ROOT / "releases" / "31e72764" / "localization"

    for name in manifest["localization_files"]:
        assert (release_dir / name).exists()
