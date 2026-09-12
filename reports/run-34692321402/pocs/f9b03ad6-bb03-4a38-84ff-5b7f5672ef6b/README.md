# Offline PoC — f9b03ad6-bb03-4a38-84ff-5b7f5672ef6b

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-local-revoke-without-chain-revoke`
- Source hint: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/lib/wallet/WalletLifecycle.tsx:50`
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
