# Offline PoC — 689b592f-6f57-4b53-9c6d-5ce0d934d6f8

- Severity: **High**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `manager/worker-configuration.gen.d.ts:411`
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
