# Offline PoC — e67a59d6-62e0-4573-bd32-0802fe7ce636

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
