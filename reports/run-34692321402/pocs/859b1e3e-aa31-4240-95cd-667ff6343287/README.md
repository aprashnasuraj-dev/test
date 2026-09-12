# Offline PoC — 859b1e3e-aa31-4240-95cd-667ff6343287

- Severity: **High**
- Asset: `workers`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `workers/api-worker/src/services/v1-names/index.ts:73`
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
