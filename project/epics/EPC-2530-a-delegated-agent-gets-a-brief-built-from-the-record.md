---
id: EPC-2530
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2560
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A delegated agent gets a brief built from the record, and a separate agent reviews its work

Realises exactly one authorising record, ADR-2560, as ADR-2730 amends it. The
epic is complete when `paw brief` prints a task's brief with its constraints
word for word and the agent definition it is written for, the implement step
states when to delegate, how to dispatch and who reviews, a delegated pull
request names the task and its brief and no agent, and a repository's own
agent replaces a shipped one.

## Acceptance criteria

Taken from ADR-2560's and ADR-2730's lists of how each will be known
realised:

1. `paw brief` on a fixture task prints its constraints word for word from
   its requirements (REQ-0812, REQ-0814).
2. `paw brief` on a fixture task prints the agent definition's name it is
   written for (REQ-1764).
3. The implement step's file names the two reasons to delegate and forbids
   the third (REQ-0826, REQ-0828).
4. A fixture review dispatch is a fresh agent and not a fork (REQ-0818).
5. The implement step's file tells a delegated pull request to name the task
   and `paw brief <task>`, and names no agent, model or vendor (REQ-1764,
   REQ-1294).
6. A project agent named like a shipped one replaces it in a fixture
   repository (REQ-2986).
7. Every requirement ADR-2560 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4945 print a task's brief with `paw brief`, in the `record` feature of `crates/meow/`
      closes: REQ-0810, REQ-0812, REQ-0814, REQ-1764

- [ ] T-002 TSK-4950 state when a step delegates, how it dispatches and who reviews, in `plugins/meow-flow/skills/method/`
      closes: REQ-0818, REQ-0824, REQ-0826, REQ-0828, REQ-2980
      depends: TSK-4945 (blocking) - the step names `paw brief`, which has to exist before the step tells anyone to run it

- [ ] T-003 [P] TSK-4955 show that a repository's own agent replaces a shipped one of the same name
      closes: REQ-2986

## Coverage

Each of the ten requirements ADR-2560 addresses lands in exactly one task, and
REQ-1764, the one ADR-2730 addresses, lands in TSK-4945. TSK-4945 and TSK-4950
are the smallest set that tests the decision, because a brief built from the
record and a step that dispatches with it are its claim. TSK-4945 and
TSK-4955 run in parallel.

## Not covered

Which steps delegate by default, which ADR-2560 leaves open. REQ-1294, which
ADR-1080 addresses and TSK-1300 closed; criterion 5 cites it because the
implement step's wording has to keep it.
