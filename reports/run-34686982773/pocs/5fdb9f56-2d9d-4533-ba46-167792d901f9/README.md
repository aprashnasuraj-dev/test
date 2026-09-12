# Offline PoC — 5fdb9f56-2d9d-4533-ba46-167792d901f9

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:11035`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
