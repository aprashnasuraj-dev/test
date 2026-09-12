# Offline PoC — 1bd5c656-a51b-41bf-9c06-3baa53e0a95d

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Base64 High Entropy String`
- Source: `workers/api-worker/wrangler.jsonc:106`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
