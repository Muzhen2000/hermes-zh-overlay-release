# Codex Remediation Prompt

Use `codex exec --full-auto` to make the smallest safe fix in the candidate checkout.

- Work only inside the provided candidate directory.
- Do not ask questions or pause for confirmation; this is a non-interactive pass.
- Keep changes minimal and targeted to the current failure.
- If you cannot fix the issue, return `status` as `blocked` and explain why in `summary`.
- Report every file you touch in `files_touched`.

The output must match the remediation output schema exactly.
