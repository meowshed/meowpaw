---
id: EPC-2860
artifact: epic
status: approved
revised: 2026-10-24
realises: ADR-3050
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The reply shape reaches every Claude Code session

Realises exactly one authorising record, ADR-3050. The epic is complete when the hook is shipped, tested and documented, and BUG-1040 names this decision under Closed by.

## Acceptance criteria

1. The hook's output carries the style's role and rules blocks as `additionalContext`, and abstains without a style file.
2. `hooks.json`, the unit's page and SPC-1240 list the hook.
3. Every requirement ADR-3050 addresses is named by a closed task.

## Tasks

- T-001 TSK-5690 print the reply shape at session start, in `plugins/meow-core/hooks/`
  closes: REQ-0930, REQ-0932

## Coverage

REQ-0930 and REQ-0932 land in TSK-5690, the one task that carries the decision.

## Not covered

BUG-1360, which the hook cannot reach.
