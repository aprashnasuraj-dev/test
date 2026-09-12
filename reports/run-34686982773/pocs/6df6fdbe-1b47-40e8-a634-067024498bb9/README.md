# Offline PoC — 6df6fdbe-1b47-40e8-a634-067024498bb9

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-eip712-domain-missing-binding`
- Source: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/machines/registration/registration.hca.actors.ts:639`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
