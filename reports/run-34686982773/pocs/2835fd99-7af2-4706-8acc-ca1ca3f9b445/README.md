# Offline PoC — 2835fd99-7af2-4706-8acc-ca1ca3f9b445

- Severity: **Medium**
- Asset: `workers`
- Rule: `detect-secrets:Base64 High Entropy String`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:21`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
