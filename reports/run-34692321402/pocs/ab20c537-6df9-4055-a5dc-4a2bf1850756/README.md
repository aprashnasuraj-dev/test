# Offline PoC — ab20c537-6df9-4055-a5dc-4a2bf1850756

- Severity: **High**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `manager/worker-configuration.gen.d.ts:1850`
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
