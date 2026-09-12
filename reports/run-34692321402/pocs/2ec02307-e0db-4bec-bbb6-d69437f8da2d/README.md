# Offline PoC — 2ec02307-e0db-4bec-bbb6-d69437f8da2d

- Severity: **High**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `manager/worker-configuration.gen.d.ts:313`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
