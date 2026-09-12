# Request-derived value is used as an outbound fetch target

**Severity:** High
**Asset:** manager
**Impact:** An attacker may redirect a server-side RPC proxy toward unintended hosts or metadata/internal services.

## Summary
A request/input-derived variable appears to select an outbound network destination.

## Vulnerability Detail
A request/input-derived variable appears to select an outbound network destination.

- Root cause: `request_controlled_rpc_upstream`
- Rule: `rpc-dynamic-fetch-url`
- Location: `worker-configuration.gen.d.ts:313`

## Impact
An attacker may redirect a server-side RPC proxy toward unintended hosts or metadata/internal services.

## Proof of Concept
```text
fetch(input
```

## Recommendation
Resolve upstreams from a fixed allowlist and reject arbitrary schemes, hosts, ports, redirects, and credentials.

## References
- None recorded
