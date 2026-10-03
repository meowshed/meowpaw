---
id: EPC-2555
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2650
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A repository declares its parts, and each verb resolves per part

Realises exactly one authorising record, ADR-2650. The epic is complete when
the profile reader layers a part's profile over the root's, `meow-checks`
resolves and reports each verb per part, each pack activates where its marker
is, and the `commit` skill and the implement step carry the rules for sparse
working trees, as SPC-1080, SPC-1040, SPC-1190 and SPC-1060 state.

## Acceptance criteria

Taken from ADR-2650's list of how it will be known realised:

1. A fixture repository with two parts resolves `test` to a different command
   in each (REQ-3042).
2. A pack whose marker sits in one part reports for that part only
   (REQ-3048).
3. Every verb report names its scope (REQ-3043).
4. Every requirement ADR-2650 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 TSK-5050 read `[parts]` and layer a part's profile over the root's, in the profile module of `crates/meow/`
      closes: REQ-0343, REQ-3040, REQ-3046

- [ ] T-002 TSK-5055 resolve and report each verb per part, with `--part` and a `scope:` line, in `plugins/meow-checks/`
      closes: REQ-0078, REQ-3042, REQ-3043, REQ-3044
      depends: TSK-5050 (blocking) - a part's verbs come from the layered profile it reads

- [ ] T-003 [P] TSK-5060 activate `meow-markdown`, `meow-mise` and `meow-gotask` per marker directory
      closes: REQ-0133, REQ-3048
      depends: TSK-5050 (not blocking) - a report names the part where one is declared, and names the directory without it

- [ ] T-004 [P] TSK-5065 carry the rules for sparse trees, root settings and read denials in the `commit` skill and the implement step
      closes: REQ-3052, REQ-3054, REQ-3056

## Coverage

Each of the twelve requirements ADR-2650 addresses lands in exactly one task.
TSK-5050 and TSK-5055 are the smallest set that tests the decision, because
a repository with two parts resolving `test` differently in each is the
claim. TSK-5060 and TSK-5065 run in parallel with each other and with
TSK-5055 once TSK-5050 has landed, and TSK-5065 can start at once.

## Not covered

How a change that spans two parts is gated, which ADR-2650 leaves to a later
decision. Guessing parts from markers alone, which ADR-2650 rules out: a
repository that declares no `[parts]` stays one part.
