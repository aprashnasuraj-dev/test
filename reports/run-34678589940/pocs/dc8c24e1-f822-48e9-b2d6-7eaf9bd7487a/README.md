# Offline PoC — dc8c24e1-f822-48e9-b2d6-7eaf9bd7487a

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `custom-xstate:undefined-target`
- Source: `transaction-manager/src/machines/transaction.machine.ts:482`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
