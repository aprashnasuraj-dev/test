# Offline PoC — 373a0778-96b8-4cff-aee8-d853c5f23a7a

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `detect-secrets:Secret Keyword`
- Source hint: `workers/api-worker/src/services/posthog/name-search-stats.test.ts:26`
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
