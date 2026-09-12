# Offline PoC — 006ccdbd-2157-44b0-98fb-92635f9224e2

- Severity: **Medium**
- Asset: `manager`
- Rule: `ui-message-origin-check`
- Source: `manager/worker-configuration.gen.d.ts:4670`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
