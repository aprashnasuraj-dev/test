# Offline PoC — 4ddeb9fb-e532-400c-88de-68b8d808c13f

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
