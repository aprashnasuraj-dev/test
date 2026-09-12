# Offline PoC — bffcb055-d35a-4b8a-bb00-976bd5dbe648

- Severity: **High**
- Asset: `manager`
- Rule: `rpc-dynamic-fetch-url`
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
