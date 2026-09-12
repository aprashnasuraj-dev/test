# Offline PoC — 2df26a9b-ba59-49ed-92b6-3095c10692a4

- Severity: **High**
- Asset: `manager`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `manager/src/utils/backend-client.ts:131`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
