# Offline PoC — ac2818c6-e9c1-438a-b2d2-48c53119d8aa

- Severity: **Medium**
- Asset: `workers`
- Rule: `trufflehog:Postgres`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/compose.yaml:24`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
