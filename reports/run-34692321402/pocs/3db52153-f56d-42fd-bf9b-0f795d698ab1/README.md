# Offline PoC — 3db52153-f56d-42fd-bf9b-0f795d698ab1

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `sast`
- Rule: `custom-xstate:undefined-target`
- Source hint: `transaction-manager/src/machines/transaction.machine.ts:602`
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
