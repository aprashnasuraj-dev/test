# Offline PoC — c80d3faf-f53c-4ac0-898c-b7057ae185cb

- Severity: **High**
- Asset: `workers`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `workers/api-worker/src/services/v1-names/index.ts:73`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
