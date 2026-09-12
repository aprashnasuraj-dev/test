# Dynamic URL reaches outbound request without observed destination validation

**Severity:** High
**Asset:** explorer
**Impact:** Impact requires reviewer confirmation from the supplied trace.

## Summary
A variable URL-like value reaches an outbound request and no nearby scheme, host, IP, or allowlist validation was observed.

## Vulnerability Detail
A variable URL-like value reaches an outbound request and no nearby scheme, host, IP, or allowlist validation was observed.

- Root cause: `server_side_fetch_of_untrusted_avatar_url`
- Rule: `custom-ssrf:dynamic-url-sink`
- Location: `worker-configuration.d.ts:402`

## Impact
Impact requires reviewer confirmation from the supplied trace.

## Proof of Concept
```text
declare function fetch(input: RequestInfo | URL, init?: RequestInit<RequestInitCfProperties>): Promise<Response>;
```

## Recommendation
Add a fail-closed validation at the identified trust boundary and add a regression test.

## References
- None recorded
