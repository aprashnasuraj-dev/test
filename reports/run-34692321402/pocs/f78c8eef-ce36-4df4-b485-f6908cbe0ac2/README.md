# Offline PoC — f78c8eef-ce36-4df4-b485-f6908cbe0ac2

- Severity: **High**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `manager/worker-configuration.gen.d.ts:1850`
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
