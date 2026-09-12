# Offline PoC — 14fbbf18-bf8d-4818-ae8d-7b29f350750b

- Severity: **High**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `manager/src/features/migration/service/v1SubgraphClient.ts:89`
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
