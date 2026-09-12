# Offline PoC — f8a0f3a1-6a13-4831-9670-eb44d8df60c2

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/machines/registration/registration.actors.ts:936`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
