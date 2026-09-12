# Offline PoC — 479d10a5-890e-48d2-b58f-39448a70a97b

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Secret Keyword`
- Source: `workers/api-worker/src/services/telegram/README.md:109`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
