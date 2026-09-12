# Offline PoC — 22a8ea50-4e03-4693-9734-c5e8217f62db

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `custom-xstate:undefined-target`
- Source: `transaction-manager/src/machines/transaction.machine.ts:519`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
