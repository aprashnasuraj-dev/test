# Offline PoC — 0ac2419e-a7cb-47f3-be3a-f04275b0b9d5

- Severity: **Medium**
- Asset: `manager`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `manager/src/features/notifications/utils/telegram/auth.ts:117`
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
