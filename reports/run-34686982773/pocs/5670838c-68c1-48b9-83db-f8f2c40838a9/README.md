# Offline PoC — 5670838c-68c1-48b9-83db-f8f2c40838a9

- Severity: **High**
- Asset: `manager`
- Rule: `rpc-dynamic-fetch-url`
- Source: `manager/worker-configuration.gen.d.ts:411`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
