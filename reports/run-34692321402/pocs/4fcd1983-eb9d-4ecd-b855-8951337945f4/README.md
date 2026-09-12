# Offline PoC — 4fcd1983-eb9d-4ecd-b855-8951337945f4

- Severity: **Medium**
- Asset: `smart-account`
- Stage: `ui`
- Rule: `ui-sensitive-web-storage`
- Source hint: `smart-account/src/providers/rhinestone/session-storage.test.ts:62`
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
