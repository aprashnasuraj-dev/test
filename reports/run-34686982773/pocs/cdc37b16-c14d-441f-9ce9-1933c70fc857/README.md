# Offline PoC — cdc37b16-c14d-441f-9ce9-1933c70fc857

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `workers/api-worker/src/services/notifications/helpers.test.ts:55`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
