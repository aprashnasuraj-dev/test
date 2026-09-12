# Offline PoC — 1638dc2d-4663-41d0-9dc7-828489cc1e37

- Severity: **High**
- Asset: `explorer`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `explorer/worker-configuration.d.ts:496`
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
