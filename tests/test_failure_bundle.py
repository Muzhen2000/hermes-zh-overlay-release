import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.collect_failure_bundle import build_failure_bundle


def test_failure_bundle_contains_required_files(tmp_path):
    bundle_dir = tmp_path / "bundle"
    mirror_dir = tmp_path / "Desktop" / "Hermes-ZH-Failures" / "latest"
    stale_file = mirror_dir / "stale.txt"
    mirror_dir.mkdir(parents=True, exist_ok=True)
    stale_file.write_text("stale\n", encoding="utf-8")

    build_failure_bundle(bundle_dir, desktop_dir=tmp_path / "Desktop")

    assert (bundle_dir / "failure-report.json").exists()
    assert (bundle_dir / "failure-report.md").exists()
    assert mirror_dir.exists()
    assert (mirror_dir / "failure-report.json").exists()
    assert (mirror_dir / "failure-report.md").exists()
    assert not stale_file.exists()

    report = json.loads((bundle_dir / "failure-report.json").read_text(encoding="utf-8"))
    assert report == {"failure_stage": "scan"}
