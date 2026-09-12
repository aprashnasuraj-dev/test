# Offline PoC — 73310a56-020c-40b9-8f24-a92e00d0907c

- Severity: **High**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `manager/worker-configuration.gen.d.ts:411`
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
