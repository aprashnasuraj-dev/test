# Offline PoC — 913f5543-652d-4800-b5fd-47fdc33af677

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/dashboard/utils/formatActivityEvent.ts:109`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
