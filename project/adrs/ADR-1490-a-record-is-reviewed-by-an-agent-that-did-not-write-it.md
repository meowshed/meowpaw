---
id: ADR-1490
artifact: adr
status: superseded
revised: 2026-09-29
addresses:
  [
    REQ-0132,
    REQ-0147,
    REQ-0149,
    REQ-0151,
    REQ-0157,
    REQ-0819,
    REQ-0822,
    REQ-0823,
    REQ-2202,
    REQ-2828,
    REQ-2830,
  ]
supersedes: []
---

# 1490. A record is reviewed by an agent that didn't write it, and its verdict is labelled as an agent's

**Superseded by ADR-2300.**

## Decision

`meow-flow` ships an agent, `record-reviewer`, that reviews one record against
a fixed set of questions for the record's kind and reports findings without
editing anything. The method skill dispatches it on every record it writes,
before it reports the gate the record waits at.

The agent's questions, one set per kind (REQ-2828):

- research: do the conclusions follow from the findings, is every source
  dated, and is the argument against the leading option stated;
- requirement: can it be tested by the check its `verification` names, does it
  carry one obligation, does it stand alone, and does it cite the research it
  elaborates;
- decision: is each alternative real and does it say why it lost, is the cost
  stated with who pays it, does something observable reverse it, and does it
  say what works after it and what still doesn't;
- specification: does a statement exist for every requirement it states, and
  is anything left that is no longer true;
- epic: would the authorising record recognise its acceptance criteria, and
  does every addressed requirement land in a task or in Not covered with a
  reason;
- task: does it say when it is done, and which evidence would close each
  requirement it cites;
- defect: does it reproduce, and does its triage say where it enters and why;
- insight: does its evidence measure something, and does its pattern hold
  past the case it came from;
- vision: does it say who the work is for and what it won't do.

The first six sets are RES-0232's list of what each kind most often misses.
The rest come from where the record already states what a kind must hold: the
decision's "what works after it" from the constitution's principle that each
decision says what works once accepted, the epic's Not covered from REQ-0266,
and the defect, insight and vision sets from their templates. A record of a
kind with no set gets only the questions every kind gets, and the report says
so.

Every kind gets two more questions: does the record mix two kinds, and does
each rule in it state its reason, where a rule with no reason is a finding
(REQ-2830). The agent asks nothing that `paw check` settles, such as an
identifier resolving or a section being present, because the mechanical part
goes through the verbs. It reports each finding as its own judgement, never as
a check that failed (REQ-0132, REQ-0147).

The agent works the way RES-0232 found a record review has to. It judges
conformance to the kind before correctness. It attacks each finding before
reporting it, and keeps a finding only where it would change what somebody
does, marking anything else as a preference. It reports a clean record as
clean in one sentence.

The agent runs with read-only tools, `Read`, `Grep` and `Glob`, so a reviewer
can't become an implementer (REQ-0819). The dispatch names the record's path
and nothing else. The agent starts with no context of its own, so it didn't
produce the record in that context and nothing tells it who did (REQ-0149,
REQ-0151).

The method skill fixes what the agent finds and dispatches a fresh agent on
the result, at most twice, because the second round catches what the first
fix broke and a bound is what makes repair end (REQ-0822). Each fresh agent
sees only the path, not the earlier findings. A finding still open after the
second round, and a finding the author rejects instead of fixing, goes into
the record under `## Open review findings`, each with the author's reason, and
the gate report names that section. The record is where the finding outlasts
the turn and where the person who approves it reads it (REQ-0823).

The agent's report opens with
`Agent review, not a person's approval; the reviewer may share the author's model family.`
The method skill's gate report says the record was reviewed by an agent and
is unreviewed by a person until someone approves it (REQ-0157, REQ-2202).
Where the session can't dispatch an agent, the skill doesn't review the record
itself: it reports the record as unreviewed by an agent or a person and stops
at the gate, because a session judging its own record is what REQ-0149
forbids. Where a person asks the session to review its own work anyway, the
result is reported as self-assessed and unreviewed by a person (REQ-0151,
REQ-2202).

This decision also settles who reviews in the method's review step, and
nothing about what that step asks of code or documentation. Where the session
produced the work under review, the step dispatches the review to an agent
with read-only tools. The verdict names itself as an agent's, never as a
person's (REQ-0149, REQ-0157).

After this decision every record the method writes reaches its gate with an
agent's answers to the questions its kind most often misses, and a person
reads them as an agent's. What still doesn't work: the questions are asked by
a model, so a finding can still be missed, and nothing but the skill's
instruction makes the session dispatch the agent.

## Why

RES-0232 found that most defects in a record are omissions, which no diff
shows because nothing was written. A fixed question per kind makes an
unanswered question visible where a missing paragraph is not. It found that a
rule with no reason can't be applied to a case its author didn't foresee, and
that the review mustn't repeat the mechanical checks as judgements.

RES-0070 found that an agent mustn't judge its own work. 17 of the 20 models
it cites judge their own output with a significant bias, 8 in their own favour
and 9 against. The effect is strongest on open-ended tasks, and capability
doesn't correct it. RES-0070 also found that a judge mustn't be told which
side it produced, that an agent's judgement can't answer whether the work
should exist, and that a same-family judge is recorded as a limitation. A fresh
agent given only the record's path meets the first two, and its opening line
meets the last two.

This repository has had its prose reviewer, an agent working from the writing
standard and not from per-kind questions, read each decision since ADR-1370
before approval. Its reports on ADR-1470, ADR-1480 and this record found
design faults the author missed, and the fixes are in each record's pull
request: a check that would fail forever on frozen records, a tree id claimed
to equal what gets merged, and this record's first fallback, which had the
session review itself against REQ-0149.

The strongest objection: an agent from the same model family as the author
still shares its blind spots, so "didn't write it" overstates the
independence. It does, and the report's opening line says so. The questions
narrow what a shared blind spot can hide, because an unanswered fixed question
is visible even to a reader who shares the blind spot.

## Alternatives

| Option                                             | Better at                                  | Why it lost                                                                                                                          |
| -------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Do nothing                                         | Costs no dispatch                          | Records reach their gate reviewed by whoever wrote them, against no questions, which RES-0232 and RES-0070 both name as the failure  |
| The session reviews its own record                 | No dispatch, cheaper                       | The author judging its own work, against REQ-0149, and the review would read as independent when it isn't                            |
| Questions in the templates, answered by the author | The author sees them while writing         | The author answers the question it thinks it answered; an omission survives exactly where the author didn't see it                   |
| A person reviews against the questions alone       | Independent of the author's model entirely | Every record would wait on a person before anyone had looked, and RES-0070 found an agent covers more and answers faster             |
| A cross-family judge                               | Independent of the author's model family   | The harness runs inside one platform, whose sessions dispatch its own models; a claim needing that strength goes to a person instead |
| Encode the questions as `paw check` rules          | Deterministic                              | Each question is a judgement, and a check that encodes one fires on the wrong thing and is switched off, against REQ-0147            |

## What it costs

`meow-flow` gains one agent, whose description sits in context on every turn.
The unit loads 385 characters on every turn today, against a budget of 500,
and a description of about 110 characters keeps it under. Each record the
method writes costs one to three agent dispatches, paid in time and tokens by
the repository running the method. The questions live in the agent's body,
which loads only when it is dispatched. A record whose findings stay open
carries a section a person has to read before approving it.

## What would reverse it

I would move the review to a person alone if, on this repository's next ten
records, the findings the agent itself marked as preferences outnumbered the
rest, counted in those records' Open review findings sections and their pull
requests. I would add a cross-family judge if the platform let a session
dispatch one.

## Consequences

- `meow-flow` ships `agents/record-reviewer.md`, with read-only tools and a
  question set per kind.
- The method skill dispatches it before reporting a gate, repairs for at most
  two rounds, records what stays open in the record, and never reviews its own
  record.
- The review step dispatches a review of the session's own work to an agent.
- SPC-1090 states the review.

## How I will know it was realised

1. `meow-author check` passes on the agent, which declares `Read`, `Grep` and
   `Glob` as its only tools, and its body carries each question set above and
   the two every kind gets, traced in the task's evidence.
2. Evaluation cases run by hand through the loop SPC-1020 states, with no
   model call in CI, show the agent reporting a draft decision with a rule
   given no reason and no cost section, opening with its label, and reporting
   a clean record as clean.
3. Evaluation cases show the method skill dispatching the agent with the path
   alone, stopping after the second round with the open findings written into
   the record, and reporting a record as unreviewed where no agent can be
   dispatched.
4. The review step carries the dispatch and the label, traced in the task's
   evidence.
5. Every requirement ADR-1490 addresses lands in exactly one closed task.

## What this does not settle

- Whether the agent's findings are right, which is the author's and the
  person's call on each one.
- What the review step asks of code and documentation, which RES-0231 and
  RES-0233 cover.
- A check that each requirement's `verification` holds one of the four kinds,
  which REQ-1662 and REQ-1664 ask for, left to a decision of its own.
