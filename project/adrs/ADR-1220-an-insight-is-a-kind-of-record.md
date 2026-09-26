---
id: ADR-1220
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0568,
    REQ-0569,
    REQ-0570,
    REQ-0571,
    REQ-0572,
    REQ-0574,
    REQ-0576,
    REQ-0577,
    REQ-0578,
    REQ-0580,
  ]
supersedes: []
---

# 1220. An insight is a kind of record, written only when something was learned

## Decision

The record gains a kind, the insight, `INS-NNNN` in `insights/`, which holds
one generalisable lesson apart from decisions, requirements and history. The
layout gives it three sections and three rules the check holds:

- Its title states the claim, carries no date and runs to at least four words,
  because a list of titles is how an insight is found.
- `## Evidence` holds a number, a measurement or a reproducible observation:
  a digit or a fenced block.
- `## What looked right` records each refuted hypothesis with why it seemed
  correct, or says none was.
- It ends with `## The pattern`, the lesson generalised past the case.

The `method` skill gains the rules no program settles: write an insight only
when something was learned, never on a schedule, with nothing learned an
ordinary outcome; keep activity in the version control history; find an
insight with `find` when the work needs it, never loaded by default; and record
a prediction in the task's acceptance criteria before the work that tests it,
where `check frozen` holds it once the task is approved.

After this decision a repository can keep what it learned, and the check
refuses an insight with no evidence or no pattern. What still doesn't work:
whether an insight is worth writing is a judgement, which evaluation would
measure and which is postponed.

## Why

RES-0018 found the one development log among six internal repositories that
earned its place: five entries in four months, each a claim-shaped title with
numeric evidence and the refuted hypotheses, holding insight and nothing else,
because activity is in the history and decisions are decision records. Its
value was proportional to how often nothing was written. The same log records
the predicted number before the fix, because without the prediction any result
reads as a success. RES-0026 found that retrieval matters by when it happens,
titles before whole documents, and names dumping whole documents into context
as the failure retrieval replaces.

The strongest objection: a kind nobody is obliged to write goes unused. It
may, and that is the finding: a log written on a schedule fills with activity,
and the method would rather keep five entries than fifty.

## Alternatives

| Option                                  | Better at                        | Why it lost                                                        |
| --------------------------------------- | -------------------------------- | ------------------------------------------------------------------ |
| A kind of record with its shape checked | Found by `find`, checked by rule | Chosen                                                             |
| A section in the decision record        | No new kind                      | A lesson outlives the decision, and REQ-0568 asks for it apart     |
| A dated log file                        | Familiar                         | A date in place of a claim, and activity the history already holds |
| Do nothing                              | Costs nothing                    | What was learned stays in a conversation and goes when it ends     |

## What it costs

A kind in the layout, three rules in the program, a template, and four rules in
the skill and the implement step.

## What would reverse it

- Insights go unwritten for a year in a repository using the method, and the
  kind is withdrawn.
- A memory the platform keeps across sessions carries insights better, and the
  kind moves there.

## Consequences

- `meow-method new insight` allocates an identifier and `template insight`
  prints its template.
- `check` holds an insight's title, evidence, refuted hypotheses and pattern.
- The `method` skill says when to write one and how to find one.

## How I will know it was realised

1. Fixtures show `check` refusing an insight whose title carries a date, whose
   evidence holds no number or block, or that doesn't end with its pattern,
   and passing one that meets each rule.
2. `meow-method template insight` prints the template, and `new insight`
   allocates `INS-0001` in an empty record.
3. Each rule ADR-1220 places in the skill and the implement step maps to its
   requirement in the task that closes it.
4. Every requirement ADR-1220 addresses lands in exactly one closed task.

## What this does not settle

- Measuring whether a model writes an insight only when something was
  learned, which waits for evaluation.
