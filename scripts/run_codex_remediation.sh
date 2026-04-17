#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <candidate_dir> <output_dir>" >&2
  exit 2
fi

CANDIDATE_DIR="$1"
OUTPUT_DIR="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$OUTPUT_DIR"

exec codex exec \
  --full-auto \
  -C "$CANDIDATE_DIR" \
  --output-schema "$ROOT_DIR/codex/remediation-output.schema.json" \
  -o "$OUTPUT_DIR/codex-last-message.md" \
  < "$ROOT_DIR/codex/remediation-prompt.md"
