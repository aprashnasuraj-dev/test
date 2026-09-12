# Offline PoC — d063d307-552c-4fc4-8f43-48a48b4b02ed

- Severity: **High**
- Asset: `manager`
- Rule: `rpc-dynamic-fetch-url`
- Source: `manager/worker-configuration.gen.d.ts:505`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
