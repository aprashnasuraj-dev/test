# Offline PoC — ebc6dcaf-4fcd-4831-bb2b-cf23d5ba663a

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `secrets`
- Rule: `detect-secrets:Secret Keyword`
- Source hint: `transaction-manager/TRANSACTION_MANAGER_SPEC.md:618`
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
