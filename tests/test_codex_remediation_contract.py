import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_codex_remediation.sh"
PROMPT = ROOT / "codex" / "remediation-prompt.md"
SCHEMA = ROOT / "codex" / "remediation-output.schema.json"


def test_codex_remediation_command_is_non_interactive():
    script = SCRIPT.read_text(encoding="utf-8")

    assert script.startswith("#!/usr/bin/env bash")
    assert "codex exec \\" in script
    assert "--full-auto \\" in script
    assert '-C "$CANDIDATE_DIR" \\' in script
    assert '--output-schema "$ROOT_DIR/codex/remediation-output.schema.json" \\' in script
    assert '-o "$OUTPUT_DIR/codex-last-message.md" \\' in script
    assert '< "$ROOT_DIR/codex/remediation-prompt.md"' in script


def test_codex_remediation_schema_is_fixed_and_machine_readable():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert schema == {
        "type": "object",
        "additionalProperties": False,
        "required": ["status", "summary", "files_touched"],
        "properties": {
            "status": {"type": "string", "enum": ["fixed", "blocked"]},
            "summary": {"type": "string"},
            "files_touched": {"type": "array", "items": {"type": "string"}},
        },
    }


def test_codex_remediation_prompt_requires_non_interactive_fixup():
    prompt = PROMPT.read_text(encoding="utf-8")

    assert "non-interactive" in prompt
    assert "codex exec" in prompt
    assert "files_touched" in prompt
