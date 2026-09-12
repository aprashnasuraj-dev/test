# Offline PoC — e9dab2fc-a9b6-42f3-9c1c-3cd3553d2f30

- Severity: **High**
- Asset: `workers`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:334`
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
