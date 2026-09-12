# Offline PoC — c3f585e3-8c4f-42a4-9b7d-4b40622123ce

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:11029`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
