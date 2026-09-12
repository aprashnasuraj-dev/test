# Offline PoC — 9388ef13-7e7b-401a-818e-6a456d130d71

- Severity: **High**
- Asset: `explorer`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `explorer/src/worker/avatar.test.ts:163`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
