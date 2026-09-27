---
id: ADR-1360
artifact: adr
status: approved
revised: 2026-09-26
addresses: []
postpones: [REQ-1138]
supersedes: []
---

# 1360. Removing an instruction is postponed until the cases can see one

## Decision

I postpone REQ-1138, which removes every instruction whose removal leaves the
measured result unchanged, until each prompt's case set can tell one rule
group's effect from noise on both models. I drop TSK-1260 from EPC-1020, with
this decision as its reason, so the epic can be verified on the three tasks
that landed.

This decision builds nothing and removes no instruction. REQ-1138 stays in
force and reads as postponed, and every verification lists it with its
condition.

After this decision `paw status` stops naming TSK-1260 as the next step, and
EPC-1020 moves to verification. What still doesn't work: instructions with no
effect stay in the shipped prompts.

## Why

The owner postponed TSK-1260 on 2026-09-24, before any run, and the task
records the two reasons. As written, the task runs about 85 removal
candidates, about 18,000 model sessions for the writing skill alone, each one
a paid model call.

The second reason is that the case sets can't see most single instructions.
The loop scores a prompt with the instruction and without it, and the delta
is the difference between those two arms. Through noise alone that delta
moves by 0.05 to 0.12. A single rule touches one or two of fifteen cases, and
three of `meow-core`'s four cases score the same in both arms on Opus 5.5. So
a removal that leaves the delta unchanged would only show that the cases
can't see the rule, and REQ-1138 would then remove most of the writing
standard, which RES-0270 never measured as having no effect. TSK-1260 records
these figures from the runs of TSK-1230.

The postponement lived only in the task's prose, so `paw status` kept naming
TSK-1260 as the next step. ADR-1330 gives a postponement its own record, and
ADR-1360 is that record.

The strongest objection: the task already proposes a cheaper plan, one rule
group at a time with ten runs per arm, so the work could resume now. It could,
but each group's result still depends on cases that can see the group, and
`meow-core` has none on Opus 5.5. Resuming before the cases exist spends the
runs and produces the result the owner postponed the task to avoid.

## Alternatives

| Option                                          | Better at                               | Why it lost                                                                             |
| ----------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------------------- |
| Postpone, and revisit at each verification      | The epic closes on the work that landed | Chosen                                                                                  |
| Resume with the amended plan, a group at a time | REQ-1138 met sooner                     | The cases can't see a group in `meow-core` on Opus 5.5, so the runs would measure noise |
| Withdraw REQ-1138                               | One fewer requirement in force          | The obligation stays true: an instruction with no effect still costs tokens             |
| Do nothing                                      | Costs nothing                           | `paw status` keeps naming a task the owner postponed, and EPC-1020 never closes         |

## What it costs

Every repository using the harness pays the tokens of each instruction with no
effect, on every turn that loads the prompt carrying it, until the condition
below holds.

## What would reverse it

I would resume the removal once each prompt's case set scores differently in
the two arms when one rule group is removed, on both Sonnet 5 and Opus 5.5, or
once the owner asks for the removal to run.

## Consequences

- `paw status` counts REQ-1138 as postponed and shows ADR-1360 as postponing
  it.
- EPC-1020 marks TSK-1260 dropped, naming ADR-1360.

## How I will know it was realised

1. `paw show REQ-1138` reads postponed by ADR-1360, and TSK-1260 dropped in
   EPC-1020.
2. `paw status` shows EPC-1020 at verification, not at TSK-1260.

## What this does not settle

- Which cases would let a case set see a single rule group, which the task
  that resumes the removal decides.
- Whether the writing skill loads its patterns for every text, the question
  TSK-1180 left open, because TSK-1260 was to measure it alongside the removal
  and nothing else measures it now.
