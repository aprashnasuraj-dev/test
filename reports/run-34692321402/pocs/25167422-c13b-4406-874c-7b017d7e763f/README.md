# Offline PoC — 25167422-c13b-4406-874c-7b017d7e763f

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `sast`
- Rule: `custom-xstate:undefined-target`
- Source hint: `transaction-manager/src/machines/transaction.machine.ts:574`
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
