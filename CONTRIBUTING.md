# Contributing

This repository publishes and maintains the Hermes Chinese overlay release system.

## Scope

- Keep changes limited to the release system.
- Do not turn this repository into a Hermes fork.
- Do not broaden the Chinese localization scope without an explicit release decision.

## Before you change anything

1. Read `release.json`, `payload/localization/support-policy.json`, and the current workflow.
2. Run `python3 -m pytest tests -q`.
3. Keep in mind that the workflow is the source of truth for promoting the supported Hermes commit and the release policy.

## What belongs here

- Release metadata
- Workflow and validation logic
- Failure bundle handling
- Release-facing documentation
- Tests for the release pipeline and repository docs

## What does not belong here

- User Hermes configuration
- API keys
- Session history or memory
- Web UI localization changes
- Direct edits to Hermes upstream behavior unless they are part of the release pipeline contract

## Change rules

- Make the smallest change that satisfies the release goal.
- Keep the failure path deterministic.
- Update or add a test for any behavior change.
- If a change affects the supported commit, use the release promotion path so `release.json` and `payload/localization/support-policy.json` stay in sync; manual edits are only for recovery and must update both files together.

## Verification

Run:

```bash
python3 -m pytest tests -q
```

If the change affects GitHub Actions or the failure bundle path, verify the workflow structure tests still pass and keep the desktop mirror path unchanged.
