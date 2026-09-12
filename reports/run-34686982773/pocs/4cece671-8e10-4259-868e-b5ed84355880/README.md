# Offline PoC — 4cece671-8e10-4259-868e-b5ed84355880

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Secret Keyword`
- Source: `workers/api-worker/compose.yaml:10`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
