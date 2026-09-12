# Offline PoC — bcbe990d-2145-4221-9f34-9ff9ab543d70

- Severity: **Medium**
- Asset: `smart-account`
- Stage: `secrets`
- Rule: `detect-secrets:Secret Keyword`
- Source hint: `smart-account/src/providers/rhinestone/initialize-account.test.ts:473`
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
