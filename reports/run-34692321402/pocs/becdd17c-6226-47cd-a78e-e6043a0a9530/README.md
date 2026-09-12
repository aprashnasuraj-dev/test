# Offline PoC — becdd17c-6226-47cd-a78e-e6043a0a9530

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `detect-secrets:Secret Keyword`
- Source hint: `workers/api-worker/compose.yaml:10`
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
