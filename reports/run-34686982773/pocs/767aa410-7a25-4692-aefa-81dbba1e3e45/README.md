# Offline PoC — 767aa410-7a25-4692-aefa-81dbba1e3e45

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `transaction-manager/src/errors/transaction.errors.test.ts:42`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
