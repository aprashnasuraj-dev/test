# Offline PoC — a0820e81-0e46-4027-9294-e017b63f354d

- Severity: **Medium**
- Asset: `explorer`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `explorer/src/components/table/EventsDataTable/TransactionEvents.tsx:12`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
