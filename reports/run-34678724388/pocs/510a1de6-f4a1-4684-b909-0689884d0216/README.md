# Offline PoC — 510a1de6-f4a1-4684-b909-0689884d0216

- Severity: **Medium**
- Asset: `manager`
- Rule: `custom-llm:prompt-injection-surface`
- Source: `manager/worker-configuration.gen.d.ts:4847`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
