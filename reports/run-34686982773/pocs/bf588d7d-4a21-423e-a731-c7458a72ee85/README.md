# Offline PoC — bf588d7d-4a21-423e-a731-c7458a72ee85

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-local-revoke-without-chain-revoke`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/renew/hooks/useRenewalTransactions.ts:169`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
