# Offline PoC — 67512556-5cfe-4c19-9168-786399b1d5c5

- Severity: **High**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `manager/worker-configuration.gen.d.ts:313`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
