# Offline PoC — da2fcb6f-3114-4991-baed-26e80a884751

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-local-revoke-without-chain-revoke`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/lib/wallet/WalletLifecycle.tsx:20`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
