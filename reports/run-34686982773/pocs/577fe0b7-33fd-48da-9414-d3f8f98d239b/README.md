# Offline PoC — 577fe0b7-33fd-48da-9414-d3f8f98d239b

- Severity: **Medium**
- Asset: `workers`
- Rule: `ui-message-origin-check`
- Source: `workers/api-worker/src/services/telegram/utils.ts:323`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
