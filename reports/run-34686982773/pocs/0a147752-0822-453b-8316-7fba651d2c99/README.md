# Offline PoC — 0a147752-0822-453b-8316-7fba651d2c99

- Severity: **High**
- Asset: `workers`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:430`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
