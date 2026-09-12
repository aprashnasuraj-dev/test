# Offline PoC — 649054b7-9e91-4228-9805-c578eff2323a

- Severity: **High**
- Asset: `manager`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `manager/worker-configuration.gen.d.ts:313`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
