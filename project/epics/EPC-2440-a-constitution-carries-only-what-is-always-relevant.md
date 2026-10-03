---
id: EPC-2440
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2570
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A constitution carries only what is always relevant, and `paw check` reports its length

Realises exactly one authorising record, ADR-2570. The epic is complete when
`paw check` reports a constitution over its target, `/meow-flow:init` and the
design step hold the rules SPC-1220 states, `meow-author:write` holds the rule
SPC-1030 states on rules that lean on being read last, and this repository's
`CLAUDE.md` carries only what SPC-1220 says a constitution carries.

## Acceptance criteria

Taken from ADR-2570's list of how it will be known realised:

1. `paw check` reports a 449-line `CLAUDE.md` as over its target and exits 0
   for it (REQ-2734).
2. `/meow-flow:init` on a fixture repository writes a constitution with no
   step of the method in it (REQ-2740).
3. Each rule in `CLAUDE.md` that must hold names its check (REQ-2732).
4. Every requirement ADR-2570 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4700 report a constitution over 200 lines from `paw check`, as advice, in the `record` feature of `crates/meow/`
      closes: REQ-2734

- [ ] T-002 [P] TSK-4710 keep the method out of an initialised constitution and ask the design step for contradicting rules, in `plugins/meow-flow/`
      closes: REQ-2738, REQ-2740

- [ ] T-003 [P] TSK-4720 forbid a shipped rule that leans on being read last, in `plugins/meow-author/skills/write/`
      closes: REQ-2742

- [ ] T-004 TSK-4730 cut this repository's `CLAUDE.md` to what is always relevant, each rule naming its check
      closes: REQ-2732, REQ-2736, REQ-2744, REQ-2745, REQ-2746
      depends: TSK-4700 (not blocking) - its report measures the cut, and the cut can be counted by hand without it

## Coverage

Each of the nine requirements ADR-2570 addresses lands in exactly one task.
TSK-4700 and TSK-4730 are the smallest set that tests the decision, because a
reported length and a constitution cut to meet it is the claim. TSK-4700,
TSK-4710 and TSK-4720 run in parallel.

## Not covered

Which rules leave `CLAUDE.md`, which ADR-2570 leaves to the cut, so TSK-4730
proposes each removal in its pull request for the owner to read.
