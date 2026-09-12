# Offline PoC — 616e34fc-59d6-4bf3-91c0-e66a6d3da31c

- Severity: **High**
- Asset: `explorer`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `explorer/worker-configuration.d.ts:306`
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
