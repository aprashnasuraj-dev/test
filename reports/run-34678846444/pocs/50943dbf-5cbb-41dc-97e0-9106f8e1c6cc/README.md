# Offline PoC — 50943dbf-5cbb-41dc-97e0-9106f8e1c6cc

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/register-v2/data/queries/hcaBudget.query.ts:113`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
