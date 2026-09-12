# Offline PoC — 3f9ee187-a08c-449b-86cf-44a4b61f37c5

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `sast`
- Rule: `custom-xstate:undefined-target`
- Source hint: `transaction-manager/src/machines/transaction.machine.ts:412`
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
