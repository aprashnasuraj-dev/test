# Offline PoC — 49d8b213-6df6-4fb6-ae62-8ed0706048d1

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-eip712-domain-missing-binding`
- Source hint: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/machines/registration/registration.hca.actors.ts:652`
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
