# Offline PoC — 407e04f5-6849-4c2b-9d36-59adea7f54aa

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/records/helpers/transformPendingChanges.ts:68`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
