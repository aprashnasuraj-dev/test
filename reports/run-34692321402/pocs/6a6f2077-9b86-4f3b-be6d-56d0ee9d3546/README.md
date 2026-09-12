# Offline PoC — 6a6f2077-9b86-4f3b-be6d-56d0ee9d3546

- Severity: **Medium**
- Asset: `explorer`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-local-revoke-without-chain-revoke`
- Source hint: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/renew/hooks/useRenewalTransactions.ts:169`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
