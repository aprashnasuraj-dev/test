# Offline PoC — 1815210c-cf63-4cd3-9f23-4829bcaafdcb

- Severity: **Medium**
- Asset: `workers`
- Rule: `trufflehog:Postgres`
- Source: `workers/workers/api-worker/compose.yaml:24`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
