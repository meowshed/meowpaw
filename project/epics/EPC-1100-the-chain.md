---
id: EPC-1100
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1130
checked-at: "#202"
---

# The method's chain, gated by the record

Realises exactly one authorising record, ADR-1130. The epic is complete when
each of the nine steps can be invoked on its own and refuses a missing or
unapproved input, `/meow-method:run` takes the record to its next gate, and the
templates ship with `meow-method`.

## Acceptance criteria

Taken from ADR-1130, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-method ready design REQ-xxxx` exits 1 naming a draft requirement, and
   0 once it is approved.
2. `meow-method status` on this repository leads with the drafts awaiting
   approval, and then shows each decision's step and the next one.
3. Run twice with no approval between, `status` prints the same state, and the
   driver says it is waiting.
4. `meow-method template task` prints `.meowpaw/templates/task.md` where that
   file exists, and the unit's template otherwise.
5. The next increment's decision in this repository is written through the
   `method` skill's design step.
6. Every requirement ADR-1130 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1420 `meow record status`, `ready` and `template`, with a
      fixture for each gate and for the state
      closes: REQ-0198, REQ-0200, REQ-0206, REQ-0210, REQ-0212, REQ-0228,
      REQ-0240, REQ-0294, REQ-0302, REQ-0321
      evidence: thirty-four fixtures, each seen failing against a stub, in
      #189.

- [x] T-002 TSK-1430 the templates moved into `meow-method`, overridable by
      the repository, with their old citations corrected
      closes: REQ-0526, REQ-0528
      evidence: the unit's template printed, and a repository's own
      preferred, in #190.
      depends: TSK-1420 - `template` resolves the path the move creates

- [x] T-003 TSK-1440 the `method` skill with a file per step, and the
      `/meow-method:run` command
      closes: REQ-0190, REQ-0192, REQ-0194, REQ-0196, REQ-0202, REQ-0204,
      REQ-0208, REQ-0532, REQ-2630, REQ-2632
      depends: TSK-1420, TSK-1430 - the steps call the program and write from
      the templates
      evidence: the skill and its nine step files pass the prompt check, and
      the unit loads 385 of its 500 characters, in #191.

## Verified

Checked under issue 202 at revision `f39d7af`, with evidence gathered there and
not carried over from the tasks. Every criterion is met:

| Criterion                                                       | Evidence at `f39d7af`                                                                                                                                                                                       |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `ready design` refuses a draft requirement, then passes      | `test_design_refuses_a_draft_requirement_and_names_it` runs `ok`: exit 1 naming the draft requirement as "draft and not approved", then 0 once approved; `ready design REQ-0190` exits 0 on this repository |
| 2. `status` leads with drafts, then places each decision        | `meow-method status` opens with "Waiting for approval" and TSK-1360, then places ADR-1130 at "next: document, then verify EPC-1100 (3 tasks done)"                                                          |
| 3. `status` prints the same twice, and the driver says it waits | Two runs of `status` are byte-identical; `/meow-method:run`, run twice in a fresh session on a record whose only decision is a draft, ran no step and reported waiting on ADR-0001 both times               |
| 4. `template` prefers the repository's own                      | `meow-method template task` prints the unit's `templates/task.md`, and `.meowpaw/templates/task.md` once that file exists                                                                                   |
| 5. The next decision is written through the design step         | ADR-1140 (#201): `ready design` exited 0 for its 36 requirements, it was written from `template adr` as a draft, and `status` led with it waiting before approval                                           |
| 6. Every requirement in one closed task, nothing outstanding    | `meow-method check`: 0 findings in all six checks, coverage included; the unit's 34 fixtures run `OK`                                                                                                       |

## Coverage

ADR-1130 addresses twenty-two requirements. Each lands in exactly one task
above, and `meow-method check coverage` compares the decision's `addresses`
against the union of the tasks' `closes`.

T-001 alone tests the decision: a gate the program holds and a state it
computes the same way twice. T-003 is where a person meets it.

## Not covered

Each artifact's full content rules, classifying trivial work, and measuring
whether the skill routes, as ADR-1130 says.
