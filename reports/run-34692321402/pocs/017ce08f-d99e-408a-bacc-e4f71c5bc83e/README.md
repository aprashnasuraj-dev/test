# Offline PoC — 017ce08f-d99e-408a-bacc-e4f71c5bc83e

- Severity: **Medium**
- Asset: `workers`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `workers/api-worker/src/app/routes/webhook/telegram.ts:14`
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
