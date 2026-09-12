# Offline PoC — 41c6dfc9-66d7-4790-9d37-76433dbaac87

- Severity: **High**
- Asset: `explorer`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `explorer/worker-configuration.d.ts:306`
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
