---
id: EPC-1380
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1400
---

# A licensing unit applies the declared header, and a program checks every file is covered

Realises exactly one authorising record, ADR-1400. The epic is complete when
`meow-licence` ships a skill that adds the declared header to a new file and a
program that fails on a file nothing covers, and this repository covers every
file it tracks.

## Acceptance criteria

Taken from ADR-1400, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-licence check` exits 0 on this repository, and fixtures show it exit
   1 on an uncovered file, on a header missing its identifier and on an
   unused licence text, and 3 on a repository declaring nothing.
2. The skill's rules carry REQ-1008, REQ-1018, REQ-1020, REQ-3066 and
   REQ-3068, traced in the task, and the prompt check passes on it.
3. A fixture shows `meow-scm check-message` passing a message that carries a
   copyright line.
4. Every requirement ADR-1400 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2110 ship `meow-licence` with its `check`, and cover every
      file this repository tracks
      closes: REQ-1022, REQ-3058, REQ-3062, REQ-3064
      evidence: nine fixtures and the check passing on this repository, in
      #444.

- [x] T-002 TSK-2120 give `meow-licence` the skill that adds the declared
      header
      closes: REQ-1008, REQ-1016, REQ-1018, REQ-1020, REQ-3066, REQ-3068
      evidence: six rules traced, and a session heading a new file, in #445.
      depends: TSK-2110 - the skill ships in the unit T-001 creates

- [x] T-003 [P] TSK-2130 show the attribution ban passes a copyright line,
      and state the cost of declaring prose in bulk
      closes: REQ-3060, REQ-3070
      evidence: the copyright fixture and the cost stated in `REUSE.toml`, in
      #446.

## Coverage

ADR-1400 addresses 12 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, a file
nothing covers fails the gate. T-003 touches neither the unit nor its program,
so it can run beside the other two.

## Not covered

Nothing ADR-1400 addresses. Documentation on public declarations and
executable examples belong with the implement step, as ADR-1400 says.
