# Offline PoC — 31222ee8-d1dd-4fcc-8115-ce08d4ff0001

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `detect-secrets:Base64 High Entropy String`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:21`
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
