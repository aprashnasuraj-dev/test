# Offline PoC — cfd925b8-b1a9-4767-8568-db24e41ce722

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
