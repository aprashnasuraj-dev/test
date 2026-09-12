# Offline PoC — a4493383-1ad1-4fa0-95cf-18fb50ce6b96

- Severity: **Medium**
- Asset: `workers`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `workers/api-worker/src/services/telegram/utils.ts:323`
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
