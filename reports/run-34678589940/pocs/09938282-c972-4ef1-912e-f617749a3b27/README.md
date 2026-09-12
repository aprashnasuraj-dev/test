# Offline PoC — 09938282-c972-4ef1-912e-f617749a3b27

- Severity: **High**
- Asset: `workers`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:1869`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
