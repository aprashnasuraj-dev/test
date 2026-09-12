# Offline PoC — cc0e4e44-abbe-4fc4-8380-5c7bb90f3bcc

- Severity: **Medium**
- Asset: `manager`
- Rule: `custom-llm:prompt-injection-surface`
- Source: `manager/worker-configuration.gen.d.ts:4848`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
