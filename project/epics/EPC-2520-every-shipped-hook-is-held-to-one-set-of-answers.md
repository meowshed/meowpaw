---
id: EPC-2520
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2450
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Every shipped hook is held to one set of answers, and the revision counter counts failures

Realises exactly one authorising record, ADR-2450, as ADR-2700 amends it. The
epic is complete when `meow-author check` holds every hook to the rules
SPC-1240 states, with the prose gate's judge as the one named exception to
the network and constant-work rules, each hook unit's README layers its
rules, the revision counter advances on a failed tool use and a pending gate
reaches the model through `SessionStart`.

## Acceptance criteria

Taken from ADR-2450's and ADR-2700's lists of how each will be known
realised:

1. `meow-author check` fails a fixture hook that answers `allow`, returns
   updated input, or calls `curl` (REQ-2720, REQ-2718, REQ-2727).
2. `meow-author check` passes `meow-prose-gate check` with its judge, and
   fails a fixture hook in any other unit whose command runs `claude -p`
   (REQ-2727, REQ-2716).
3. `meow-author check` fails a unit whose README doesn't describe its hook
   (REQ-2726).
4. A fixture tool use that fails advances the revision counter in
   `meow-checks`' run state (REQ-2728).
5. The `SessionStart` hook's output names a pending gate in a fixture with
   one (REQ-2730).
6. Every requirement ADR-2450 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4900 hold every hook to SPC-1240's check list in `meow-author check` and the crate's hook subcommands
      closes: REQ-2716, REQ-2718, REQ-2720, REQ-2722, REQ-2724, REQ-2726, REQ-2727

- [ ] T-002 TSK-4905 write each hook unit's `## Hooks` section with its gate check and skill, and show a crashing hook abstains
      closes: REQ-2710, REQ-2712, REQ-2714
      depends: TSK-4900 (not blocking) - the check reads the section this task writes, and either can land first

- [ ] T-003 TSK-4910 advance a revision counter in `meow-checks` on every tool use, failed ones included
      closes: REQ-2728
      depends: TSK-4900 (not blocking) - the new hook must pass the check, and the check's rules can be met by hand before it lands

- [ ] T-004 [P] TSK-4915 pin that `meow-flow`'s `SessionStart` output names a pending gate
      closes: REQ-2730

## Coverage

Each of the twelve requirements ADR-2450 addresses lands in exactly one task,
and the three ADR-2700 addresses, REQ-2716, REQ-2727 and REQ-2728, land in
TSK-4900 and TSK-4910. TSK-4900 and TSK-4910 are the smallest set that tests
the decision, because a check that fails a hook breaking the rules and a
counter that counts a failure are its two claims. TSK-4900 and TSK-4915 run
in parallel.

## Not covered

Which hooks the units should have, which ADR-2450 leaves open. A hook that
builds a network call at run time, which the check can't see and review
holds.
