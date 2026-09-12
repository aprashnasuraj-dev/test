# Offline PoC — 6a381553-9bce-4466-b63d-b56ed148ffb1

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `transaction-manager/tsconfig.tsbuildinfo:1`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
