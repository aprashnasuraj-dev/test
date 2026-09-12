# Offline PoC — a6458dff-2eb5-416e-b9e1-c204e2f5ac01

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `secrets`
- Rule: `detect-secrets:Secret Keyword`
- Source hint: `transaction-manager/src/machines/registration/registration.actors.test.ts:41`
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
