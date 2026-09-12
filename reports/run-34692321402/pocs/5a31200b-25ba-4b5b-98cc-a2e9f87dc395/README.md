# Offline PoC — 5a31200b-25ba-4b5b-98cc-a2e9f87dc395

- Severity: **Medium**
- Asset: `workers`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `workers/api-worker/src/services/telegram/utils.ts:369`
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
