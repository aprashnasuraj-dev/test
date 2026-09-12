# Offline PoC — 9edb43e4-6c9e-46f1-9373-870780c0a9e8

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `secrets`
- Rule: `detect-secrets:Secret Keyword`
- Source hint: `transaction-manager/src/helpers/getSmartAccountAddress.test.ts:23`
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
