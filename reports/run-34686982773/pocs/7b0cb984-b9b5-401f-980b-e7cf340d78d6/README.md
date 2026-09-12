# Offline PoC — 7b0cb984-b9b5-401f-980b-e7cf340d78d6

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-eip712-domain-missing-binding`
- Source: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/machines/registration/registration.hca.actors.ts:641`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
