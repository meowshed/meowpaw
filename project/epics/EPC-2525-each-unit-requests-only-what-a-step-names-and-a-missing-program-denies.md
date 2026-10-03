---
id: EPC-2525
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2460
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Each unit requests only what a step names, and a hook whose program is missing denies

Realises exactly one authorising record, ADR-2460, as ADR-2710 amends it. The
epic is complete when `meow-author check` fails a tool no step is named for,
every blocking hook's launcher denies when its binary is missing, a crate
test holds the harness's writes to its run state and the record, and the
kernel's output style states the secrets rule.

## Acceptance criteria

Taken from ADR-2460's and ADR-2710's lists of how each will be known
realised:

1. `meow-author check` fails a fixture agent whose README names no step for
   one of its tools (REQ-1432).
2. A gate task whose tool is missing exits non-zero with the tool's name
   (REQ-1426).
3. With no binary beside it, `meow-git`'s launcher denies a `git commit` with
   exit 2 and a reason naming `meow-git` and its install command, and the
   same holds for `meow-prose-gate`, `meow-github` and `meow-loop`
   (REQ-1426).
4. With no `meow-scm`, a push is still let through with the message check
   reported unrun (REQ-0079).
5. The kernel's instructions state the secrets rule (REQ-1424).
6. Every requirement ADR-2460 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4920 fail a tool no step is named for, in `meow-author check`, and name each tool's step in every unit's README
      closes: REQ-1430, REQ-1432

- [ ] T-002 [P] TSK-4925 deny from every blocking hook's launcher when its binary is missing, naming the install command
      closes: REQ-1426

- [ ] T-003 [P] TSK-4930 fail a subcommand that writes outside the run state and the record, in a crate test
      closes: REQ-1429

- [ ] T-004 [P] TSK-4935 state the secrets rule in `meow-core`'s output style, within its budget
      closes: REQ-1424

## Coverage

Each of the five requirements ADR-2460 addresses lands in exactly one task,
and REQ-1426, the one ADR-2710 addresses, lands in TSK-4925. TSK-4920 and
TSK-4925 are the smallest set that tests the decision, because a tool traced
to its step and a missing program that stops the call are its two checkable
claims. All four tasks run in parallel.

## Not covered

REQ-1420 and REQ-1422, the confirmation before an irreversible action, which
ADR-2460 leaves to the unattended chain. A proof that the harness never reads
a secret, which no program can give, so REQ-1424 rests on the instruction and
on review.
