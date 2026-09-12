# Offline PoC — 1ff412ee-fa15-40e6-a6cb-e3f457459c04

- Severity: **High**
- Asset: `manager`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `manager/worker-configuration.gen.d.ts:1850`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
