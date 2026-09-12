# Offline PoC — 29eea41b-912b-48fd-a25f-280b3e17bf25

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:10893`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
