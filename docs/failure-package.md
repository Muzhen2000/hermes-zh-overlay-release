# Failure Package

`collect_failure_bundle.py` writes the minimal release failure package used by Task 5.

The bundle directory contains:

- `failure-report.json`
- `failure-report.md`

The same two files are mirrored to:

- `~/Desktop/Hermes-ZH-Failures/latest`

The JSON report is intentionally minimal for now and records the failure stage:

```json
{"failure_stage":"scan"}
```

The markdown report is a human-readable entry point for the next person taking over the failure.
