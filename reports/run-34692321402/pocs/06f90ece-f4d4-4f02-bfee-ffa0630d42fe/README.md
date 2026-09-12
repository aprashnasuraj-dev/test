# Offline PoC — 06f90ece-f4d4-4f02-bfee-ffa0630d42fe

- Severity: **High**
- Asset: `explorer`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `explorer/worker-configuration.d.ts:402`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
