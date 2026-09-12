# Offline PoC — 13499712-d4ba-4b8a-884d-206ec32a2b89

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Basic Auth Credentials`
- Source: `workers/api-worker/.dev.vars.example:2`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
