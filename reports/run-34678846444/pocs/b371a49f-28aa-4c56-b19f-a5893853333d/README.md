# Offline PoC — b371a49f-28aa-4c56-b19f-a5893853333d

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `custom-xstate:undefined-target`
- Source: `transaction-manager/src/machines/transaction.machine.ts:574`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
