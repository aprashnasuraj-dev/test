# Offline PoC — 5a8ef2a9-680d-416d-b6cf-d6db0cf9a3a5

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/register-v2/data/queries/hcaBudget.query.ts:127`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
