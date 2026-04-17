import json
import sys
from types import SimpleNamespace
from pathlib import Path

import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_candidate import build_candidate
from scripts.check_upstream import check_upstream
from scripts.validate_candidate import validate_candidate
from payload.scripts.hermes_zh_overlay_manager import (
    decide_local_target,
    mirror_failure_bundle,
)
from scripts import check_upstream as check_upstream_module


def load_workflow(relative_path: str) -> dict:
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def test_release_json_exposes_single_supported_commit():
    release_payload = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
    support_policy = json.loads(
        (ROOT / "payload" / "localization" / "support-policy.json").read_text(encoding="utf-8")
    )

    assert release_payload["supported_commit"]
    assert release_payload["supported_commit"] == support_policy["supported_commit"]
    assert release_payload["official_repo"] == support_policy["upstream_repo"]
    assert release_payload["official_repo"] == "https://github.com/NousResearch/hermes-agent.git"
    assert release_payload["failure_bundle"]["desktop_path"] == "~/Desktop/Hermes-ZH-Failures/latest"


def test_check_upstream_flags_commit_drift():
    changed = check_upstream(official_latest="new", supported_commit="old")
    unchanged = check_upstream(official_latest="same", supported_commit="same")

    assert changed == {
        "official_latest": "new",
        "supported_commit": "old",
        "needs_release": True,
    }
    assert unchanged == {
        "official_latest": "same",
        "supported_commit": "same",
        "needs_release": False,
    }


def test_build_candidate_materializes_candidate_dir(tmp_path):
    state = check_upstream(official_latest="new", supported_commit="old")
    candidate_dir = tmp_path / "candidate"

    result = build_candidate(state, candidate_dir)

    assert candidate_dir.exists()
    assert result == {
        "needs_release": True,
        "candidate_commit": "new",
        "candidate_dir": str(candidate_dir),
    }


def test_validate_candidate_requires_zero_missing_and_zero_control():
    result = validate_candidate(
        scan_summary={"missing": 0, "control": 0},
        tests_ok=True,
        overlay_ok=True,
    )

    assert result == {"publishable": True, "failure_stage": None}


def test_validate_candidate_blocks_on_scan_drift():
    result = validate_candidate(
        scan_summary={"missing": 2, "control": 0},
        tests_ok=True,
        overlay_ok=True,
    )

    assert result == {"publishable": False, "failure_stage": "scan"}


def test_local_maintain_reads_release_truth_not_origin_main():
    result = decide_local_target(
        release_supported_commit="abc123",
        origin_main_commit="def456",
    )

    assert result == "abc123"


def test_local_sync_mirrors_failure_bundle_to_desktop(tmp_path):
    desktop = tmp_path / "Desktop"
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "failure-report.md").write_text("# failed\n", encoding="utf-8")

    target = mirror_failure_bundle(bundle, desktop_root=desktop)

    assert target == desktop / "Hermes-ZH-Failures" / "latest"
    assert (target / "failure-report.md").exists()


def test_workflow_routes_failed_candidate_to_failure_bundle():
    workflow = load_workflow(".github/workflows/unattended-release.yml")

    on_block = workflow.get("on", workflow.get(True))
    assert workflow["name"] == "unattended-release"
    assert on_block["schedule"][0]["cron"] == "0 * * * *"
    assert "workflow_dispatch" in on_block

    candidate = workflow["jobs"]["candidate"]
    assert candidate["runs-on"] == "macos-latest"

    steps = candidate["steps"]
    assert steps[0]["uses"] == "actions/checkout@v4"

    step_names = [step.get("name") for step in steps if "name" in step]
    assert step_names.index("Collect failure bundle") < step_names.index("Codex exec remediation")
    assert step_names.index("Collect failure bundle") < step_names.index("Upload failure bundle artifact")

    steps_by_name = {step["name"]: step for step in steps if "name" in step}

    assert steps_by_name["Detect upstream"]["run"] == "python3 scripts/check_upstream.py"
    assert steps_by_name["Build candidate"]["run"] == "python3 scripts/build_candidate.py"
    assert (
        steps_by_name["Validate candidate"]["run"]
        == "python3 scripts/validate_candidate.py --overlay-ok --tests-ok --scan-missing 0 --scan-control 0"
    )
    assert steps_by_name["Codex exec remediation"]["if"] == "${{ failure() }}"
    assert "bash scripts/run_codex_remediation.sh candidate out || true" in steps_by_name["Codex exec remediation"]["run"]
    assert steps_by_name["Collect failure bundle"]["if"] == "${{ failure() }}"
    assert steps_by_name["Collect failure bundle"]["run"] == "python3 scripts/collect_failure_bundle.py"
    assert steps_by_name["Upload failure bundle artifact"]["if"] == "${{ failure() }}"
    assert steps_by_name["Upload failure bundle artifact"]["uses"] == "actions/upload-artifact@v4"
    assert steps_by_name["Upload failure bundle artifact"]["with"]["name"] == "hermes-zh-failure-bundle"
    assert steps_by_name["Upload failure bundle artifact"]["with"]["path"] == "out/failure-bundle"

    script_steps = ("Detect upstream", "Build candidate", "Validate candidate")
    for step_name in script_steps:
        run = steps_by_name[step_name]["run"]
        assert "python - <<'PY'" not in run
        assert "supported_commit=release[\"supported_commit\"]" not in run

    all_uses = [step.get("uses", "") for step in steps]
    assert all("actions/create-release" not in use for use in all_uses)
    all_runs = [step.get("run", "") for step in steps]
    assert all("gh release" not in run for run in all_runs)


def test_fetch_official_latest_rejects_empty_output(monkeypatch):
    def fake_run(*args, **kwargs):
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(check_upstream_module.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="returned no refs"):
        check_upstream_module.fetch_official_latest("https://example.invalid/repo.git")
