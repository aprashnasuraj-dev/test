# Offline PoC — 17b22922-5ee2-491d-b0cc-288195a65ade

- Severity: **High**
- Asset: `explorer`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `explorer/worker-configuration.d.ts:1841`
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
