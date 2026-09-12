# Offline PoC — b4a6a170-218a-445f-beb9-f2f6f60e5d36

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `detect-secrets:Base64 High Entropy String`
- Source hint: `workers/api-worker/wrangler.jsonc:106`
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
