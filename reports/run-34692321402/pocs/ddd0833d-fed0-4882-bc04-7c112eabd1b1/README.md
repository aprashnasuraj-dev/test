# Offline PoC — ddd0833d-fed0-4882-bc04-7c112eabd1b1

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `secrets`
- Rule: `detect-secrets:Hex High Entropy String`
- Source hint: `transaction-manager/tsconfig.tsbuildinfo:1`
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
