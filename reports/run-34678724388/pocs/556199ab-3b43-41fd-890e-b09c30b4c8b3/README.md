# Offline PoC — 556199ab-3b43-41fd-890e-b09c30b4c8b3

- Severity: **Medium**
- Asset: `workers`
- Rule: `custom-llm:prompt-injection-surface`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:4846`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
