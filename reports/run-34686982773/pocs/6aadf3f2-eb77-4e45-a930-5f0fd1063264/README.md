# Offline PoC — 6aadf3f2-eb77-4e45-a930-5f0fd1063264

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Hex High Entropy String`
- Source: `workers/api-worker/wrangler.jsonc:27`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
