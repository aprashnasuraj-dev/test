# Offline PoC — f1465082-88ad-47a9-bfc8-28fe8ec20514

- Severity: **Medium**
- Asset: `manager`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `manager/src/features/notifications/utils/telegram/auth.ts:76`
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
