# Offline PoC — ddd9bd86-b498-48be-ada1-df7af9b9906b

- Severity: **High**
- Asset: `explorer`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `explorer/worker-configuration.d.ts:1841`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
