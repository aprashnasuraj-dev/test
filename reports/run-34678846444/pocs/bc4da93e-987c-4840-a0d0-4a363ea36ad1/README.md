# Offline PoC — bc4da93e-987c-4840-a0d0-4a363ea36ad1

- Severity: **Medium**
- Asset: `workers`
- Rule: `custom-llm:prompt-injection-surface`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:4847`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
