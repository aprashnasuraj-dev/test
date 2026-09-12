# State transition targets undefined state: error.reverted

**Severity:** Medium
**Asset:** transaction-manager
**Impact:** Impact requires reviewer confirmation from the supplied trace.

## Summary
A parsed machine transition targets a state not defined in the same states block.

## Vulnerability Detail
A parsed machine transition targets a state not defined in the same states block.

- Root cause: `xstate_dead_transition`
- Rule: `custom-xstate:undefined-target`
- Location: `src/machines/transaction.machine.ts:574`

## Impact
Impact requires reviewer confirmation from the supplied trace.

## Proof of Concept
```text
confirming -> error.reverted
```

## Recommendation
Add a fail-closed validation at the identified trust boundary and add a regression test.

## References
- None recorded
