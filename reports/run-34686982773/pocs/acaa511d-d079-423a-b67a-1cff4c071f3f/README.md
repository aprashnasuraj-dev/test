# Offline PoC — acaa511d-d079-423a-b67a-1cff4c071f3f

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/machines/registration/registration.hca.actors.test.ts:268`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
