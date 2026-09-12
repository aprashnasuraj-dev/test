# Offline PoC — ff7356b2-e1e6-42e4-86b3-1c3bff2221c5

- Severity: **High**
- Asset: `workers`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:1869`
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
