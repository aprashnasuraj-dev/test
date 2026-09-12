# Offline PoC — 9e3fbad7-b096-4488-8d26-9a176ecf83ce

- Severity: **Medium**
- Asset: `workers`
- Rule: `ui-message-origin-check`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:4669`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
