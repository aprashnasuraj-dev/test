# Offline PoC — 0e450f36-69f3-4b83-8ecb-5519b22df0f9

- Severity: **High**
- Asset: `explorer`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `explorer/worker-configuration.d.ts:306`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
