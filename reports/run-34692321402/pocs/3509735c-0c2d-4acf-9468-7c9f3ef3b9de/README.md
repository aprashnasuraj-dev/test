# Offline PoC — 3509735c-0c2d-4acf-9468-7c9f3ef3b9de

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `trufflehog:Postgres`
- Source hint: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/compose.yaml:24`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
