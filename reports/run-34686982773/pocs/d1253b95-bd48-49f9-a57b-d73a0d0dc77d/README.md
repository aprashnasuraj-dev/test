# Offline PoC — d1253b95-bd48-49f9-a57b-d73a0d0dc77d

- Severity: **High**
- Asset: `explorer`
- Rule: `rpc-dynamic-fetch-url`
- Source: `explorer/worker-configuration.d.ts:402`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
