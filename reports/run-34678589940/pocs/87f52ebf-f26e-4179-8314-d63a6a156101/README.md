# Offline PoC — 87f52ebf-f26e-4179-8314-d63a6a156101

- Severity: **Medium**
- Asset: `explorer`
- Rule: `custom-llm:prompt-injection-surface`
- Source: `explorer/worker-configuration.d.ts:4818`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
