---
id: EPC-2330
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2400
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Each subcommand of the native tool makes one determination, with pinned output and a manual equivalent

Realises exactly one authorising record, ADR-2400. The epic is complete when
a test holds every subcommand of `meow` to output lines that change only
through a breaking commit and to help that names its manual equivalent, and
the method's step files call a subcommand for each mechanical determination,
as SPC-1080 states under "Each subcommand makes one determination".

## Acceptance criteria

Taken from ADR-2400's list of how it will be known realised:

1. A test lists every `paw` subcommand and fails for one whose help doesn't
   name the manual equivalent (REQ-1176).
2. A test per subcommand pins its output lines, and changing one fails it
   (REQ-1184).
3. The step files cite a subcommand for each count, coverage, staleness and
   resolution they need, and a check finds no step that asks the model to
   count by reading (REQ-1172).
4. Every requirement ADR-2400 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 TSK-4330 pin every `paw` subcommand's output lines and name its manual equivalent in its help, in the `record` feature
      closes: REQ-1170, REQ-1174, REQ-1176, REQ-1182, REQ-1184

- [ ] T-002 [P] TSK-4340 pin the output lines and name the manual equivalent of every other unit's subcommand
      closes: REQ-1176, REQ-1184
      depends: TSK-4330 (not blocking) - both add the same kind of test, and the second can copy the first's form or write its own

- [ ] T-003 [P] TSK-4350 name the subcommand for each mechanical determination in the method's step files, and state how its output is cited
      closes: REQ-1172, REQ-1178, REQ-1180, REQ-1190

## Coverage

Each of the nine requirements ADR-2400 addresses lands in a task. REQ-1176
and REQ-1184 land in two, because `paw` and the other units' subcommands are
two reviewable changes. TSK-4330 alone tests the decision, because `paw` is
the helper every step of the method calls. TSK-4340 and TSK-4350 run in
parallel with it and with each other.

## Not covered

REQ-1188 and a structured output format, because ADR-2400 leaves both to a
later decision.
