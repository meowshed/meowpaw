---
id: EPC-1580
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-1620
checked-at:
---

# The chain gains a cover step, and paw ready gates the implementation on the task's Cover

Realises exactly one authorising record, ADR-1620. The epic is complete when
`paw ready` knows ten steps and refuses to implement a task whose `## Cover`
isn't filled, `paw status` names cover before implement, and every prompt the
method ships reads ten steps and says where each step's artifact lands.

## Acceptance criteria

Taken from ADR-1620, from its list of how I will know it was realised, before
the tasks below were written:

1. `paw ready bogus TSK-0001` exits 2 and names the ten steps in order.
2. On a fixture record, `paw ready cover` exits 0 on an approved task under an
   approved epic, and 1 on a draft task and on a task whose dependency isn't
   done.
3. `paw ready implement` exits 1 naming the missing Cover on an approved task
   with none, 1 naming the path on a Cover whose failing run doesn't exist, 1
   naming the path on a Cover with a check that doesn't exist, 1 naming the
   line on a Cover whose `Landed in` is `none` while `Checks` names a path, 1
   naming the criterion on a `Judgement` entry with no reason, 0 once the
   section is filled, and 0 on a task whose `Judgement` names every criterion
   with a reason and whose `Checks`, `Failing run` and `Landed in` are `none`.
4. On a fixture where a task is marked `[x]` with no `## Cover`, `paw check`
   reports nothing about it, and `paw check frozen` reports nothing on an
   approved task whose only change is a filled Cover.
5. On a fixture with an approved epic and an open task with no Cover,
   `paw status` prints `next: cover`; with the Cover filled it prints
   `next: implement`; run twice unchanged, its output is identical.
6. `paw check` accepts a defect with `enters: cover` that names what it
   violates, and reports one that names nothing.
7. A static fixture reads `method/SKILL.md`, finds the ten step names in order
   in its body and its description, and finds one file under `steps/` for
   each. The budget check passes on `meow-flow`.
8. A static fixture reads each step file's role and finds the committed file
   ADR-1620's table gives, and for review finds that it writes nothing into
   the repository.
9. The next epic this repository implements keeps one run of
   `/meow-flow:run` whose output shows `next: cover <task>`, then
   `next: implement <task>`, and ends at a gate, and that task's Cover and
   Evidence were filled by the run.
10. Every requirement ADR-1620 addresses, REQ-3200, REQ-3202, REQ-3203,
    REQ-3207 and REQ-3216, lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2530 give `crates/meow/src/record.rs` ten steps, a `cover`
      gate, an `implement` gate on the filled Cover, the frozen exemption
      for `## Cover` and a defect entering at `cover`
      closes: REQ-3207, REQ-3216
      evidence: 16 checks seen failing at the cover commit 0c9cec6, and 170
      `meow-flow` fixtures passing, in #616.

- [ ] T-002 [P] TSK-2540 make `paw status` name cover before implement, and
      let `/meow-flow:run` continue past a step with no gate
      closes: REQ-3202
      depends: TSK-2530, because `status` decides between cover and
      implement with the Cover reading that task adds

- [ ] T-003 [P] TSK-2550 add `steps/cover.md`, name ten steps in
      `method/SKILL.md`, and name in each step's role where its artifact lands
      closes: REQ-3200, REQ-3203
      depends: TSK-2530, because the prompts tell the model to run the
      cover gate, which `paw ready` refuses with exit 2 until that task
      lands

TSK-2540 and TSK-2550 touch different files except `meow-flow`'s version and
its README's `describes`, so whichever lands second takes the next minor
version above the first.

## Coverage

ADR-1620 addresses five requirements, and each lands in one task. REQ-3207 and
REQ-3216 land in TSK-2530, because `paw ready implement` is what refuses a
task whose Cover lacks the failing run or leaves a criterion unnamed.
REQ-3202 lands in TSK-2540, because the driver and the `status` line it reads
are what take a task through cover and implement in one invocation. REQ-3200
and REQ-3203 land in TSK-2550, because both are static obligations on the
prompts: the ten steps the skill names, and the file each step's role names.

The smallest set that tests the decision is TSK-2530 and TSK-2540: with them,
the program refuses an uncovered task and the driver names cover, which is
what REQ-3200's step changes in practice. Before any task is finished,
criterion 1 can be measured: `paw ready bogus X` names nine steps today and
must name ten.

Criterion 9 rests on the next epic this repository implements after the three
tasks land, so no task here closes it. The verify step checks it, and names it
as unmet if no such run exists yet, as REQ-3170 requires.

Once TSK-2530 lands, `paw ready implement` refuses TSK-2540 and TSK-2550 until
their `## Cover` is filled. Their implementer fills it by hand in the four
lines ADR-1620 gives, before the implementation, because `steps/cover.md`
doesn't exist until TSK-2550 lands. Each of the three tasks carries a `## Cover`
section reading `Not yet.` for that reason, ahead of the template change.

## Not covered

- The cover step's content rules, REQ-3204, REQ-3206, REQ-3208, REQ-3210,
  REQ-3211 and REQ-3213, which ADR-1620 leaves to the decision that addresses
  them.
- Running cover and implement in separate contexts, REQ-3214 and REQ-3215,
  and holding the cover step's checks read-only during implementation,
  REQ-3212, which ADR-1620 names as not settled.
- Checking that the kept run failed and that the checks landed before the
  implementation, REQ-3206 and REQ-3208, for the same reason.
- The user-facing pages that name nine steps: `plugins/meow-flow/README.md`
  beyond its `describes`, the root `README.md` and `llms.txt`. The document
  step updates them once every task is done, from ADR-1620's consequences.
