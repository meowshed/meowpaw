---
id: ADR-2200
artifact: adr
status: superseded
revised: 2026-09-29
addresses: [REQ-0314, REQ-2070, REQ-2078, REQ-3520, REQ-3522, REQ-3524]
postpones: []
supersedes: []
---

# 2200. A skeptic tries to refute each requirement an epic claims before it is verified, and a confirmed refutation becomes a draft defect

**Superseded by ADR-2300.**

## Decision

`meow-flow` ships a second agent, `skeptic`, and the verify step dispatches it
on every epic before recording the epic verified (REQ-3522). The agent tries
to show that each requirement the epic's authorising record addresses is
unmet. The verifier checks each refutation it reports, and writes each one it
confirms as a draft defect record (REQ-3524). This amends ADR-1160 in one
respect: REQ-3520 replaces REQ-0542, so verification may write a draft defect
besides the epic's `## Verified` section and its `checked-at`, and changes no
stored status. Everything else ADR-1160 decided about the verify step stands.

### The agent

`plugins/meow-flow/agents/skeptic.md` follows `record-reviewer`'s form. Its
tools are `Read`, `Grep` and `Glob` and nothing else, so it can't change what
it judges (REQ-0819). Its dispatch names the epic's identifier and nothing
else, so it isn't told who did the work or what the verifier concluded
(REQ-0149). It reads the epic, the record that authorises it, each requirement
that record addresses, each task's `## Evidence` and `## Cover`, the checks
those sections name and the code the checks exercise. Everything it reads is
data, and it follows no instruction found in it, because the party it judges
wrote the epic, the evidence and the code, and an instruction there would let
that party steer its own judge.

For each requirement it asks two questions, the two ways RES-0309 found
verified requirements in this repository turning out unmet:

1. Would each check that closes the requirement still pass against a wrong
   implementation? The agent looks for a weak assertion, a tautology, a mock
   of the thing under test, output matched loosely, and a search or pattern
   that can match nothing, as BUG-1170's did (REQ-2070).
2. Does the behaviour meet the requirement's own text on every input the text
   covers? The agent looks for the input no check tries, such as an absent
   optional field, an entry with an extra mark or an empty list, which BUG-1210,
   BUG-1180 and BUG-1250 each turned out to be.

It reports each requirement in one of three states, and never as met, because
the model monitors RES-0309 cites missed between 35% and 58% of the shortcuts
on multi-file work:

- `refuted`, naming the input or condition that breaks the requirement, how
  the verifier can confirm it, and what would fix it. Confirming means one of
  two things: a command whose run shows the break and writes nothing into the
  repository, or the lines of a check that show it can't fail. Where the fault
  is a check, the fix is to rewrite that check, never to add a second one
  beside it (REQ-2078).
- `not refuted`, naming what it tried.
- `not judged`, naming what it couldn't reach, such as a check that isn't in
  the repository.

Before it reports a refutation it attacks it, as the review step attacks a
finding (REQ-0314). It keeps a refutation only where it can name the input and
the requirement's text covers that input; a refutation that rests on a reading
the text doesn't support is dropped. Its report opens with the label
`record-reviewer` uses,
`Agent review, not a person's approval; the reviewer may share the author's model family.`,
because the verifier and the person approving the epic have to know whose
judgement they hold (REQ-0157).

### The verify step

The step dispatches `meow-flow:skeptic` once it has found every acceptance
criterion met and before it writes `## Verified`, so no section claims the
epic verified before anyone tried to refute it. It dispatches once per
verification. Verification applies no fix, so a second dispatch would read
the same tree; a later verification, after a fix lands, dispatches a fresh
agent. The verify run that follows review returning the work dispatches no
skeptic, for the same reason: no fix has landed, so the tree is the one the
skeptic already read, and that run acts only on the refutation review named. A
task's own verification dispatches nothing, because an epic is where
requirements are claimed realised and an epic isn't verified by verifying
each task again (REQ-0299).

For each refutation the verifier runs the command it names, where that
command writes nothing into the repository, or reads the lines it names. A
refutation whose command would write into the repository is treated as a
claim about the lines it names and confirmed by reading them, or rejected as
malformed where it names none, because the verifier writes nothing but what
REQ-3520 permits:

- A refutation the run or the lines bear out is confirmed. The verifier writes
  a draft defect from `paw template bug` with `violates` naming the
  requirement, the refutation's input and what the verifier ran or read as its
  reproduction with the revision it was confirmed at, the run's output as what
  the system does, and a `severity`, which REQ-0372 makes a property of the
  observation. Where an open defect already names that requirement and a
  reproduction that fails for the same cause, it cites that defect in
  `## Verified` and writes no second one. It leaves `## Triage` empty and sets
  no `enters`, because deciding whether the work or the requirement is wrong
  is a person's judgement (REQ-3524, RES-0063). Where the fault is a check, the defect names
  the check as the thing that's wrong and says it is rewritten (REQ-2070,
  REQ-2078). The requirement is reported as a gap, and the epic is recorded
  verified only as REQ-3170 allows: naming the criterion the defect
  contradicts, the defect, and why closing is right.
- Where the verifier judges that closing over the defect isn't right, it
  writes no `## Verified` section and no `checked-at`, so the epic stays at
  verify. The step stops at the defect's approval gate and names the draft
  defect. A person triages and approves it, its fix runs as the defect's own
  task on the defect's path (ADR-1440), and `/meow-flow:run` then runs verify
  on the epic again, as `paw status` names it, with a fresh skeptic.
- A refutation the verifier doesn't bear out is rejected, with the command it
  ran or the lines it read, and the reason.

`## Verified` gains a `Refutation` paragraph naming the dispatch, each
requirement not refuted or not judged, each confirmed refutation with its
defect, and each rejected one with its reason. Where the session can't
dispatch an agent, the paragraph reads `Refutation: not attempted, no agent
could be dispatched`, names the cause, and the report says so (REQ-3522). The epics verified
before this decision keep their sections as written, because the paragraph is
an obligation on the step and no program checks old sections for it.

The step writes nothing else: no code, no requirement, no specification and
no fix (REQ-3520, REQ-0319).

### The review step

The verifier is usually the session that did the work, so a rejection is that
session disagreeing with the agent that checked it. REQ-0824 resolves such a
disagreement in a fresh context, and the review step already runs as a fresh
agent that reads the verification first. It gains one rule: judge each
rejected refutation, and where it sides with the skeptic, return the work to
verify naming that refutation. Review can return the work only over a
refutation the verifier rejected by reading lines. Where the verifier ran the
command a refutation named and the run showed no break, review reports its
disagreement as a finding and doesn't return the work, because a run outranks
two readings. The verify step treats a refutation the review returned the
work over as confirmed. No run showed the break in that case, so its draft
defect records, as what the system does, review's reasoning and the lines
review read, marked as not reproduced by a run.

That path writes a defect no run confirmed, which the Alternatives table
rejects for an unconfirmed refutation. The difference is a second reader: an
unconfirmed refutation is the skeptic's claim alone, while here two agents,
one of them in a fresh context, read the same lines of a check and agree that
it can't fail. The marking tells the person triaging it that no run backs it.

### What works after this, and what doesn't

After this decision, an epic reaches review with each of its requirements
attacked by an agent that didn't do the work, on the two questions that let
four verified requirements through here. Each confirmed attack is on disk as a
draft defect that authorises nothing until a person triages and approves it.

What still doesn't work:

- A requirement reported `not refuted` may still be unmet, because the agent
  finds some breaks and misses others.
- An orchestration that runs the verify step inside a subagent gets no
  refutation, because a subagent can't dispatch another (REQ-0820). Its
  `## Verified` says `not attempted`, so the gap is visible and not hidden.
- The verifier confirms refutations of its own work. Only a rejection reaches
  a fresh context, through review.
- A refutation that needs code changed to demonstrate, such as a mutation of
  the implementation, can only be confirmed by reading.
- A draft defect written after review returned the work rests on two agents'
  reading of a check's lines, not on a run, and may be wrong in a way no run
  has tested.

## Why

RES-0309 found four requirements this repository had recorded as verified
that were unmet: one on a check that matched nothing and exited 0, three on
an input the requirement's text covered and no check tried. Each got past the
verify step, which runs in the session that implemented the work. RES-0070
found 17 of 20 models judging their own output with a significant bias, so
REQ-0288's question, asked by the implementer about its own checks, is the
case the method already refuses for records (ADR-1490).

RES-0309 also found that a second reader adds detection and proves nothing:
monitors caught 86% to 89% of shortcuts on single-function tasks and 42% to
65% on multi-file ones. That is why the agent's best verdict is `not refuted`,
and why each refutation has to name something the verifier can run or read:
the verifier then confirms on evidence, and a refutation that neither a run,
the lines of a check nor review's reading of them bears out never becomes a
defect.

A confirmed refutation is evidence that a requirement isn't met, which is what
a defect record holds (ADR-1440), and the method keeps durable findings in the
record and not in the conversation. REQ-0542 stopped verification writing one,
while REQ-3170 already let an epic close over a defect only where it is
recorded. The reason RES-0063 gave for a read-only verification is that
deciding whether the code or the requirement is wrong belongs to a person. A
draft defect with its triage left empty keeps that reason and drops the rule
that went further than it.

The agent's tools are read-only because ADR-1490 settled that for
`record-reviewer` and REQ-0819 requires it. The plan this decision started
from gave it `Bash` to run a unit's program on a scratch directory. `Bash`
writes anywhere, so the agent could become an implementer whenever it chose,
and the verifier runs the named command anyway. RES-0309 records
that I couldn't observe the platform enforcing the allowlist on this machine,
so that rests on the documentation RES-0263 read.

The strongest objection: the verifier that confirms or rejects refutations is
the biased party. A confirmation rests on a run or on the lines of a check,
which the verifier reports and the person can read. A rejection is the
dangerous direction, and it goes to review, which runs in a fresh context and
reads the reason.

## Alternatives

| Option                                                             | Better at                                         | Why it lost                                                                                                             |
| ------------------------------------------------------------------ | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                         | No dispatch, no new agent                         | The verify step keeps judging its own work, which let four verified requirements through here                           |
| The verify step asks the two questions itself                      | No dispatch, no budget                            | The implementing session judging its own checks, which REQ-0149 forbids and RES-0070 measured                           |
| The agent gets `Bash` and runs its own reproductions               | A refutation arrives already demonstrated         | A reviewer with a tool that writes, against REQ-0819; the verifier can run the named command itself                     |
| Keep REQ-0542; report a confirmed refutation and let a person file | No requirement withdrawn                          | The finding lives only in the conversation, and REQ-3170 already asks for the defect to be recorded                     |
| Every refutation becomes a defect, unconfirmed                     | No biased filter between the agent and the record | No false-refutation rate is known, and an unreproduced claim would enter the record as evidence                         |
| Refute in the review step                                          | Review already attacks findings                   | Review writes nothing (REQ-0544), so a refutation there can't become a defect, and the epic would already read verified |
| Dispatch per task                                                  | Smaller reads per dispatch                        | Verifies the epic by verifying its tasks again, against REQ-0299, and multiplies the dispatches                         |
| Two rounds per verification, as for records                        | Catches what a first round missed                 | A round follows a fix, and verification applies none, so a second dispatch reads the same tree                          |
| A fresh agent confirms each refutation                             | No biased party between the skeptic and a defect  | A confirmation rests on a run or a check's lines the person can read; only a rejection needs a fresh context, in review |

## What it costs

Every repository that installs `meow-flow` keeps the agent's description in
context on every turn: `mise run budget` printed `meow-flow: 487 of 500
characters on every turn` on `main` after #622, and the agent's description
is held to 100 characters at most, so its budget rises to 600. Each epic verification costs one dispatch that
reads the epic's requirements, checks and code, paid in time and tokens by the
repository running the method. The verifier pays one run or one read per
refutation, and the person approving pays for triaging each draft defect,
including any that a triage closes as `rejected`. Review reads one more
paragraph, and judges each rejected refutation.

## What would reverse it

- I would remove the agent if, over this repository's next ten epic
  verifications, defects filed within eight weeks of the tenth one show more
  requirements those ten recorded `not refuted` to be unmet than the agent's
  refutations confirmed across the same ten. The agent would then miss more
  than it finds, and cost a dispatch on every epic for it.
- I would have a fresh agent confirm refutations too if, over the same ten,
  review sided with the skeptic on more than one rejected refutation. The
  verifier's filter would then be measurably biased.
- I would drop the confirmation and write every refutation as a draft defect
  if a published measurement put a same-family skeptic's false-refutation rate
  below one in ten.

## Consequences

- `meow-flow` ships `agents/skeptic.md` with read-only tools, the input rule,
  both questions, the three states and the label, and its README names the
  agent.
- `steps/verify.md` dispatches it before writing `## Verified`, writes a draft
  defect for each confirmed refutation, stops at the defect's gate where
  closing over it isn't right, and records the `Refutation`
  paragraph; its rule V2 states REQ-3520, and its rule V9 records the outcome
  in `## Verified` and `checked-at` in place of a stored status.
- `steps/review.md` judges each rejected refutation and returns the work to
  verify where it sides with the skeptic.
- `meow-flow` rises one minor version, its README's `describes:` follows, and
  its `budget.toml` rises to 600.
- SPC-1090 states the agent and the dispatch. It states REQ-3520 in place of
  REQ-0542 from this change on, because a living specification can't cite a
  withdrawn requirement, and today's verify step already meets REQ-3520.
- Three evaluation cases in `plugins/meow-flow/evals/`, with thresholds in
  `thresholds.toml` set before the first run.

## How I will know it was realised

1. `meow-author check` passes on `agents/skeptic.md`, whose tools are `Read`,
   `Grep` and `Glob` alone, and a static fixture in `plugins/meow-flow/tests`
   finds in its body the input rule, both questions, the three states, the
   rule that it attacks each refutation before reporting it, the rule that a
   faulty check is rewritten and not supplemented, and the label.
2. A static fixture finds, in `steps/verify.md`, the dispatch named before the
   step that writes `## Verified`, the draft defect with empty triage, the
   `Refutation` paragraph and its `not attempted` form, and REQ-3520 in V2; and
   in `steps/review.md`, the rule on rejected refutations.
3. An evaluation case gives the agent an epic whose closing check is a
   tautology and grades that it reports that requirement `refuted`, naming the
   check's lines. A second gives it a sound epic and grades that it reports no
   refutation. A third gives the verify step a confirmed refutation and
   grades that it writes a draft defect whose `violates` names the
   requirement, whose reproduction names the refutation's input and its
   revision, with a `severity`, `## Triage` empty and no `enters`. All three run by hand on
   Sonnet 5 and Opus 5.5, with Opus 5.5 judging, at thresholds set before the
   first run.
4. `paw check` accepts a draft defect with `violates` and `severity` set, a
   reproduction, an empty `## Triage` and no `enters`, shown by a fixture.
5. Every requirement ADR-2200 addresses lands in exactly one closed task.

## What this does not settle

- Which model the agent runs on. It inherits the session's, although the
  monitoring study found Opus 4 more sensitive than Sonnet 4.
- A skeptic for a single task, or for work no epic covers.
- How a refutation is confirmed where demonstrating it needs the code changed.
- Whether the orchestration that asked for this stage now drops its own copy.

## Open review findings

- Round 2 suggested trimming the Decision to the choice and its limits,
  because SPC-1090 states the agent, its states and the confirmation. I kept
  the detail, because each part carries the reason it was chosen, which the
  specification doesn't hold, and this record freezes on approval while the
  specification is rewritten; the specification states the present, and this
  record states what was chosen and why.
