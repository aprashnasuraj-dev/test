# Offline PoC — 681b88bf-4027-472f-bef2-b3869c6d96a7

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-unscoped-session-authority`
- Source: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/types/signer.types.ts:39`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
