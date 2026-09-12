# Offline PoC — 6b21cf45-8279-48f8-ab59-2ef79d6ea128

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Secret Keyword`
- Source: `workers/api-worker/src/app/routes/names/index.test.ts:55`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
