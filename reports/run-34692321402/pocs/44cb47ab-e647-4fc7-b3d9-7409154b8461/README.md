# Offline PoC — 44cb47ab-e647-4fc7-b3d9-7409154b8461

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `trufflehog:Postgres`
- Source hint: `workers/workers/api-worker/compose.yaml:24`
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
