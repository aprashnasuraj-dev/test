# Offline PoC — b3fa7c1c-6474-4661-b16b-fea9cd17fe67

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
