# Offline PoC — 2de44e50-a3e5-404a-b5f3-d211422ba9f1

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Secret Keyword`
- Source: `workers/api-worker/src/services/posthog/name-search-stats.test.ts:26`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
