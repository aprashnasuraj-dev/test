# Offline PoC — 1c1f88e2-61ef-4368-ba72-bf9edac04a0b

- Severity: **Medium**
- Asset: `workers`
- Rule: `ui-message-origin-check`
- Source: `workers/api-worker/src/app/routes/webhook/telegram.ts:14`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
