# State transition targets undefined state: error.preparation

**Severity:** Medium
**Asset:** transaction-manager
**Impact:** Impact requires reviewer confirmation from the supplied trace.

## Summary
A parsed machine transition targets a state not defined in the same states block.

## Vulnerability Detail
A parsed machine transition targets a state not defined in the same states block.

- Root cause: `xstate_dead_transition`
- Rule: `custom-xstate:undefined-target`
- Location: `src/machines/transaction.machine.ts:412`

## Impact
Impact requires reviewer confirmation from the supplied trace.

## Proof of Concept
```text
preparing -> error.preparation
```

## Recommendation
Add a fail-closed validation at the identified trust boundary and add a regression test.

## References
- None recorded
