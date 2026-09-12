# Offline PoC — 91168167-fb3a-45d3-8215-90a1c4252c51

- Severity: **High**
- Asset: `explorer`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `explorer/src/worker/avatar.ts:10`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
