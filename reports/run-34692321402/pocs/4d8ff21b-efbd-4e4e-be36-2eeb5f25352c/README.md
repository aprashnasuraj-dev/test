# Offline PoC — 4d8ff21b-efbd-4e4e-be36-2eeb5f25352c

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `secrets`
- Rule: `detect-secrets:Hex High Entropy String`
- Source hint: `transaction-manager/src/errors/transaction.errors.test.ts:42`
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
