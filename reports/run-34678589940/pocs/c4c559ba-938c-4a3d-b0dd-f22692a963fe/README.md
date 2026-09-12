# Offline PoC — c4c559ba-938c-4a3d-b0dd-f22692a963fe

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `custom-xstate:undefined-target`
- Source: `transaction-manager/src/machines/transaction.machine.ts:602`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
