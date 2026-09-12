# Offline PoC — 1e2f6f84-932c-48b7-a8d5-0e017d6bc976

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-local-revoke-without-chain-revoke`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/lib/wallet/WalletLifecycle.tsx:50`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
