# Offline PoC — 3f86e5e5-40f5-4a2c-8054-e6f0fc1350b5

- Severity: **Medium**
- Asset: `workers`
- Stage: `secrets`
- Rule: `detect-secrets:Hex High Entropy String`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:11053`
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
