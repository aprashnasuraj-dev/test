# Offline PoC — 85332a33-804c-49db-b134-2bc3a90cd675

- Severity: **High**
- Asset: `manager`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `manager/src/utils/backend-client.ts:132`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
