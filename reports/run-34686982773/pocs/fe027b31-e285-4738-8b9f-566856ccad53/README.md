# Offline PoC — fe027b31-e285-4738-8b9f-566856ccad53

- Severity: **High**
- Asset: `workers`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `workers/api-worker/src/services/delivery/push.ts:111`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
