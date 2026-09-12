# Offline PoC — 73e0994a-2c73-436e-b456-77f30e9d76bb

- Severity: **High**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `manager/worker-configuration.gen.d.ts:505`
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
