# Failure Package

`collect_failure_bundle.py` writes the minimal release failure package used by the GitHub workflow.

Local `maintain` failures also write a desktop mirror automatically:

```text
~/Desktop/Hermes-ZH-Failures/latest
```

The bundle directory contains:

- `failure-report.json`
- `failure-report.md`

The same two files are mirrored to:

- `~/Desktop/Hermes-ZH-Failures/latest`

The GitHub workflow JSON report records the failure stage:

```json
{"failure_stage":"scan"}
```

The local maintain JSON report records the command, schedule mode, current head, supported commit, dirty-file summary, and error message. The markdown report is a human-readable entry point for the next person taking over the failure.
