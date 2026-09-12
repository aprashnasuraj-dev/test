# Offline PoC — e7993f58-5cc2-4092-ae00-abb39d9cdf60

- Severity: **Medium**
- Asset: `workers`
- Rule: `ui-message-origin-check`
- Source: `workers/api-worker/src/services/telegram/utils.ts:369`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
