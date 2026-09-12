# Offline PoC — 46e20fa9-709a-4ceb-8e66-861a7af5110d

- Severity: **High**
- Asset: `manager`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `manager/worker-configuration.gen.d.ts:411`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
