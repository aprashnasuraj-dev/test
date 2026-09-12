# Offline PoC — 2193b90e-5e3e-48b7-aa6c-ec14e234bbf6

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `sast`
- Rule: `custom-xstate:undefined-target`
- Source hint: `transaction-manager/src/machines/transaction.machine.ts:519`
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
