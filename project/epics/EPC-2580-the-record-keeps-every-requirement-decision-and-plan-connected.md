---
id: EPC-2580
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2740
---

# The record keeps every requirement, decision and plan connected

Realises ADR-2740. The epic is complete when `paw check` rejects either
missing relation, the current record has neither, and TOML comments are pinned.

## Acceptance criteria

1. A fixture approved requirement with no approved provider produces one
   finding naming the requirement.
2. A fixture approved addressing ADR with no approved epic or direct task
   produces one finding naming the ADR.
3. Superseded, withdrawn and postponing-only records do not produce either
   finding.
4. A profile with comments parses.
5. Every newly addressed requirement lands in a closed task or is named under
   Not covered with its existing evidence.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [ ] T-001 TSK-5140 report an active requirement without a provider and an
      active decision without a plan, in the `record` feature
      closes: REQ-3900, REQ-3902
- [ ] T-002 [P] TSK-5145 pin comments in the profile parser
      closes: REQ-3800

## Coverage

TSK-5140 closes the two graph obligations and TSK-5145 closes the retained
profile obligation.

## Not covered

The 30 carried requirements need no new implementation: their original tasks
already closed them, and SPC-1040, SPC-1090 and SPC-1201 still state them.
ADR-2740 restores only the provider relation those implementations lost.
