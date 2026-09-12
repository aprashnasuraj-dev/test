# Offline PoC — 60198cb3-02d3-414e-ab00-a3fa3193d043

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `detect-secrets:Secret Keyword`
- Source: `transaction-manager/TRANSACTION_MANAGER_SPEC.md:618`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
