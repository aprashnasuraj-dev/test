# Offline PoC — da0d1b25-c284-4114-8bc1-15ccef92db65

- Severity: **Medium**
- Asset: `explorer`
- Rule: `ui-message-origin-check`
- Source: `explorer/worker-configuration.d.ts:4641`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
