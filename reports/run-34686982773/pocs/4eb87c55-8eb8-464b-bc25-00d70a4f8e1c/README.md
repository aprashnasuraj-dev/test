# Offline PoC — 4eb87c55-8eb8-464b-bc25-00d70a4f8e1c

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/renew/hooks/useRenewalTransactions.ts:215`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
