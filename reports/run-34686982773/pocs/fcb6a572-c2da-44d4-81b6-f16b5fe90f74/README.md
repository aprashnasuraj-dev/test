# Offline PoC — fcb6a572-c2da-44d4-81b6-f16b5fe90f74

- Severity: **Medium**
- Asset: `manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `manager/worker-configuration.gen.d.ts:1923`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
