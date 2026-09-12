# Offline PoC — 10d51e1e-8b25-41b7-b016-02f8b7a6dc20

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
