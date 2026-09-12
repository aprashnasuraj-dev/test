# Offline PoC — 7fba1497-3d5f-4e6c-b709-d7dce348dd6b

- Severity: **Medium**
- Asset: `explorer`
- Rule: `custom-llm:prompt-injection-surface`
- Source: `explorer/worker-configuration.d.ts:4819`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
