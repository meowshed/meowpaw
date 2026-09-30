---
id: ADR-2300
artifact: adr
status: approved
revised: 2026-09-29
addresses:
  [
    REQ-3600,
    REQ-3602,
    REQ-3604,
    REQ-3606,
    REQ-3608,
    REQ-3610,
    REQ-3612,
    REQ-3614,
    REQ-3616,
    REQ-3618,
    REQ-3620,
    REQ-3622,
    REQ-3624,
    REQ-3626,
    REQ-3628,
    REQ-3630,
    REQ-3632,
    REQ-3634,
    REQ-3636,
    REQ-3638,
    REQ-3640,
    REQ-3642,
    REQ-3644,
    REQ-3646,
    REQ-3648,
    REQ-3650,
    REQ-3652,
    REQ-3654,
  ]
postpones: []
supersedes: [ADR-1490, ADR-1530, ADR-1550, ADR-1560, ADR-2200]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2300. A requirement closes with the tasks that name it, and the chain keeps no verification, no evidence and no record review

## Decision

A requirement is closed when a closed task or epic names it and no open one
does, and it has no state after closed (REQ-3600, REQ-3602). A requirement no
task or epic names is open (REQ-3608), and one an open defect names in
`violates` is open again until the defect closes (REQ-3610). A task or an epic
names any number of requirements, and a requirement is named by any number of
tasks and epics (REQ-3648). Every requirement a decision addresses is named by
at least one of them or postponed (REQ-3646). `paw` derives all of it from the
marks already in the record, so nobody writes a verdict.

The chain becomes seven steps (REQ-3638):

```text
research -> requirements -> design -> spec -> epic -> implement -> review
```

Verify goes. Cover folds into implement: a task's pull request first adds its
tests, at least one for each criterion a program can check, in a commit of
their own where they fail (REQ-3616, REQ-3640, REQ-3642). The implementation
follows and leaves those tests alone, or changes one only in a commit of its
own saying why it was wrong (REQ-3644). The same pull request carries the
documentation and the record marks the task changes (REQ-3618). Its merge
closes the task, the epic where the task was the last open one, and each
requirement nothing open still names (REQ-3604). A task is marked done only in
a change whose gate passed (REQ-3606), and the gate is the whole of
verification. The task template loses its `## Cover` section, and `paw ready
implement` stops reading one.

Review is an agent's code review inside the task's pull request. The pull
request fixes what it finds, and the review writes nothing into the record
(REQ-3626). The review reports each test that would still pass against a wrong
implementation (REQ-3612), which is the question the verify step and the
skeptic asked, now asked where the test and the code sit side by side. No agent reviews a record (REQ-3624), and the person approving the
pull request is its reader.

A decision's research, requirements, decision record, specification
changes, epic and tasks land together in one pull request, with the approved
records they replace withdrawn in it (REQ-3650). Merging that pull request is
the approval.

A decision one task realises gets that task and no epic: the task names
`realises: ADR-NNNN` in place of `epic:` (REQ-3630). An acceptance criterion
must be decidable from its own task's or epic's work (REQ-3628).

The repository keeps no run output (REQ-3614): `project/evidence/` goes,
`meow-verbs evidence --keep` goes, and a task's Evidence section names the
checks it ran and its pull request.

`paw status` lists each postponed requirement with its reversal condition on
every run (REQ-3622), and never names a step whose work has landed (REQ-3620).
The documentation check reports a living page stating a step count other than
the method's (REQ-3632).

Every existing record is migrated to the new shape in the epic that realises
this, as a mechanical change of its own: tasks lose `## Cover`, epics lose
`## Verified`, `checked-at` and `## Open review findings`, and a citation of a
kept run becomes the pull request it ran under (REQ-3652). The migration
rewrites approved records, which the amendment path forbids for content; this
decision authorises it for these sections alone, because the owner judged it
a change of format and not of data: the sections record the old chain's
ceremony, not what anyone decided, and `paw count` before and
after goes in the change.

`meow-method`, the stub `meow-flow` replaced one release ago, leaves the
marketplace (REQ-3654). No other unit loses its purpose: `meow-unattended`,
`meow-prose-gate` and the packs serve the chain as it now stands.

`meow-verbs` becomes `meow-checks`, and `meow-verbs` stays one release as a
stub that says so (REQ-3634, REQ-3636). The profile's `[verbs]` table and the
five verb names stay, so no repository's profile changes.

This supersedes ADR-1490 (record review), ADR-1530, ADR-1550 and ADR-1560
(kept evidence) and ADR-2200 (the skeptic). It amends ADR-1330 in one respect,
the point where postponements are revisited, which becomes every status
report; ADR-1620, whose cover step folds into implement; and ADR-1310, which
projects a task with no epic as an issue with no parent.

Once accepted, the record states the new rules and the approved requirements
they replace are withdrawn, and nothing in the tree has changed. Once the
epic lands, a requirement's state comes from its tasks, the chain has seven
steps, and the repository holds no evidence files. What still doesn't work:
nothing mechanical tells a test that can't fail; the code review judges it.

## Why

Records, not waiting, are the cost: a pull request merges in a median of 3.5
minutes, while the cover step took eleven pull requests and 8,677 lines, 47% of
them records written before any code (RES-0310). Verification, the one step
that wrote a verdict by hand, stalled on a criterion nobody could meet, and
kept evidence added as many lines as every authored record together
(RES-0310). The owner instructed that verification is the passing tests, that
the repository holds no evidence, that no agent reviews records, that cover is
writing the tests before the code, that a requirement closes with its tasks
and reopens with a defect, and that tasks, epics and requirements relate many
to many.

`meow-checks` says what the unit does for its reader. `meow-gate` names the
same role and collides with the method's approval gate, which the
constitution defines in the same documents. `meow-checks` collides with the
`check` verb, a smaller collision, since that verb is one of five commands the
unit runs and its page names all five together (RES-0310).

## Alternatives

| Option                                       | Better at                                             | Why it lost                                                                                                                 |
| -------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                   | Costs no change, keeps a second reader of every claim | Verification of EPC-1580 can't pass as the record stands, and the owner named both verification and record review as stalls |
| Trim the ceremony and keep every step        | Changes no policy                                     | Keeps the prose verification and record review, the two costs named                                                         |
| Derive a verified state from a recorded pass | Keeps "verified" distinct from "closed"               | Needs a store for the pass that every reader sees alike, and the owner asked for no verification record                     |

## What it costs

The second reader goes. RES-0309 found four requirements recorded as verified
that were unmet, and closing on the task would have called them closed too, so
such a defect is found later by ordinary work. The 765 requirements now
verified and 19 closed and unverified all become closed, so "verified" stops
meaning anything the record can show. A program no longer refuses changes to
tests written first, and no second context writes them, so the discipline
rests on the commit order and the review. The rename touches about 20 live
files.

## What would reverse it

- A defect record showing a requirement closed by this rule that a verify step
  with a second reader would have caught before the merge, twice within one
  release.
- A repository adopting the harness asking for kept evidence to satisfy an
  audit it is subject to.

## Consequences

- **Corrected by EPC-2200.** 51 approved requirements are withdrawn: the 47
  below, and four verification rules withdrawn while the epic's prompts were
  written, on what an unrealised decision, a task list, and checking the
  record apart from verifying the work each meant.
- 47 approved requirements are withdrawn by tombstone in the change that
  proposes this decision, each naming its replacement where one exists: the
  verification step's rules, the documentation step's, review after
  verification, the verified-needs-a-check pair, kept evidence, record
  review, the cover step's rules, the ten steps, the one-task coverage rule,
  the closing of an epic with a recorded defect, and the three skeptic rules.
  The grouping rule stands, since a task with no epic writes no grouping.
- The five superseded decisions carry a tombstone naming this one.
- The specifications that stated the withdrawn requirements drop them in the
  same change: SPC-1040, SPC-1080, SPC-1090 and SPC-1100.
- EPC-2100's two tasks are dropped with this decision as the reason, and
  EPC-1580 closes with its tasks.
- The method skill, its step files, the task, epic and bug templates, the
  constitution's chain and the root README change.
- `crates/meow/src/record.rs` changes how it derives state, how `ready` and
  `status` read the chain, and its coverage rule.

## How I will know it was realised

1. On a fixture record, `paw show` reports a requirement closed when its only
   task is done, open when one of two tasks naming it is open, open when no
   task names it, and open when an open defect violates it.
2. On a fixture where one requirement is named by two tasks and one task
   names three requirements, `paw check coverage` reports nothing.
3. `paw status` prints no `verified` count, no `verify`, `document` or
   `cover` step, and lists each postponed requirement with its condition.
4. `paw ready bogus TSK-0001` names seven steps, and `method/SKILL.md` names
   the same seven.
5. `paw ready implement` accepts a task with no `## Cover` section, and
   `project/evidence/` doesn't exist.
6. `paw check` accepts a task that names `realises: ADR-NNNN` and no epic.
7. The documentation check fails a fixture page naming a step count other
   than seven.
8. `claude plugin install meow-verbs@meowpaw` still works and says it is
   deprecated in favour of `meow-checks`.
9. No file under `plugins/meow-flow/` dispatches `record-reviewer` or
   `skeptic`.
10. No record under `project/` carries `## Cover`, `## Verified`,
    `checked-at` or `## Open review findings`.
11. `meow-method` is not in the marketplace.
12. Every requirement this decision addresses is named by a closed task.

## What this does not settle

- Whether a program can tell a test that can't fail. The code review judges
  it (REQ-3612), and a mechanical check, such as running the tests against a
  mutated implementation, is a later decision.
- What happens to the history of `project/evidence/`. The files leave the
  tree, and git keeps them; nothing rewrites history.

Three questions the research left open are settled here. A pass needs no
store, because a task closes only by merging with its gate passed. The unit
is `meow-checks`. The constitution keeps "approval gate" for a stop and "the
gate" for the checks, since the new name frees "gate" from the unit and every
use in the constitution already carries its qualifier.
