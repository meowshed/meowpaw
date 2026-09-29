---
id: TSK-2702
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1651
closes: [REQ-0816]
issue: 701
projected: 94131e36b55a
---

# Make each shipped agent report one of four outcomes, and make its dispatcher act on the word

`record-reviewer`, `prose` and `router` each write `outcome:`, a space and one of
`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` and `BLOCKED` on a line of its
own, `meow-author check` fails a unit's agent that doesn't name all four, and
the method skill and the review step act on the word before they read the
rest. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given fixture agents in a unit's `agents/` directory, when
   `meow-author check` reads them, then it fails, naming the file and each
   missing word, on one naming none of the four and on one missing only
   `BLOCKED`, and passes on one naming all four and on a repository agent
   under `.claude/agents/` naming none. Closed by: crate tests in
   `crates/meow/src/author.rs`, whose failing fixtures are seen failing
   against the current check before the rule lands, kept as a failing run.
2. Given this change's tree, when `mise run prompts` and `meow-author check`
   run, then both exit 0 with all three shipped agents naming the four
   words. Closed by: the kept evidence of the `lint` verb, which runs the
   `prompts` task.
3. Given `plugins/meow-flow/agents/record-reviewer.md`,
   `plugins/meow-prose/agents/prose.md` and
   `plugins/meow-flow/agents/router.md`, when each is read, then each states
   when it reports each of the four outcomes and where the outcome line and
   the cause go, as SPC-1030 states under "What an agent reports", and the two
   reviewers carry the rule that quotes nothing beyond the span a finding
   names, 25 words at most. Closed by: fixtures in
   `plugins/meow-flow/tests/test_record.py` and
   `plugins/meow-prose/tests/` that find each rule, and the `prompts` check.
4. Given `plugins/meow-flow/skills/method/SKILL.md`, when it is read, then a
   rule beside M22 and M23 acts on the reviewer's outcome by SPC-1090's table
   under "The review before a gate", dispatches once more after
   `NEEDS_CONTEXT` and no more, reads the line allowing leading space, and
   reports a return with no outcome line from the set as unreviewed by an
   agent. Closed by: a `MethodSkill` fixture in
   `plugins/meow-flow/tests/test_record.py` that finds each part, seen
   failing first.
5. Given `plugins/meow-flow/skills/method/steps/review.md`, when it is read,
   then W13 dispatches `record-reviewer` for each record the change writes
   and `prose` for each other prose text, names each by its path, or as text
   where it has no file, keeps a picked read-only agent for the code, and
   reports a review from either of the two agents with no outcome line as not
   run. Closed by: a fixture in `plugins/meow-flow/tests/test_record.py` that
   finds each part, seen failing first.
6. Given the evaluation cases `clean-requirement`,
   `decision-missing-its-reasons` and `route-a-tiny-fix` in
   `plugins/meow-flow/evals/` and `decision-without-reason` in
   `plugins/meow-prose/evals/`, when a person runs each three times, then the
   outcome line matches
   `^\s*outcome: (DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED)$` on the
   second line of `record-reviewer`'s report and the first line of `prose`'s
   and `router`'s in at least two runs of three, and each reviewer's report is
   under 4,000 characters. Closed by: judgement, because the graders run a
   model by hand and never in CI; the kept transcripts are the evidence, and a
   hand-run result is a smoke check and not a rate.
7. Given a hand-run case under `claude -p --permission-prompts none` that
   starts the method skill's review of a record path that doesn't exist, when
   a person runs it, then the stream shows exactly two dispatches of
   `record-reviewer`, each report carrying `outcome: NEEDS_CONTEXT`, and the
   gate report calls the record unreviewed by an agent and names the brief it
   sent. Closed by: judgement, because a person runs the case and reads the
   kept stream.
8. Given a hand-run case under the same flags that replaces `record-reviewer`
   with a repository agent whose definition says nothing of an outcome, when
   a person runs it, then the agent's report holds no line matching the
   pattern in criterion 6, and the gate report calls the record unreviewed by
   an agent. Closed by: judgement, because a person runs the case and reads
   the kept stream.
9. Given this change's tree, when the five verbs run through
   `meow-verbs run`, then each passes. Closed by: the kept evidence of that run.

## What to do

Write into each of the three shipped agents the outcome rule SPC-1030 states
under "What an agent reports": the four words, when that agent reports each,
by the rows SPC-1090 gives it, and where the outcome line and the cause line
go. `record-reviewer` keeps its fixed label as its first line. `router` gives
`outcome:` as its first field and `cause:` after it. Give `record-reviewer`
the quoting rule `prose` already holds under V1, at 25 words. Leave the denial
rule to TSK-2703; the `BLOCKED` row here says only when the agent reports it.

Add to `meow-author check` the rule SPC-1030 states under "The check": an
agent in a unit's `agents/` directory whose body doesn't name all four
outcomes fails, naming each missing word, and a repository's own agent isn't
read for it. Write the failing fixtures first and keep the run that shows
them failing.

Add to the method skill a rule beside M22 and M23 that acts on each outcome
as SPC-1090's table under "The review before a gate" says, including the
single second dispatch after `NEEDS_CONTEXT`, and reads a return with no
outcome line from the set as unreviewed by an agent. Rewrite W13 in
`steps/review.md` as SPC-1090 states in the paragraph after that table. Keep
the method skill's core within `budget.toml`.

If `plugins/meow-flow/skills/route/SKILL.md` exists when this task starts,
write the router's rows from SPC-1090 under "The route" into it. If it
doesn't, say so in Evidence, because TSK-3510 then writes them.

Add a regex grader for the outcome line to each of the four evaluation cases
criterion 6 names, and one for the report's length to the three reviewer
cases. Add the hand-run cases for criteria 7 and 8 under
`plugins/meow-flow/evals/`, each with a `prompt.md`, its settings, graders and
a line in `thresholds.toml`. Neither runs in CI.

Raise `meow-flow`'s, `meow-prose`'s and `meow-author`'s minor versions,
because each gains a capability, and match each README's `describes:`. If
another change raised one first, take the next minor above it.

## Depends on

Nothing. ADR-1710 and EPC-1651 are approved, and SPC-1030 and SPC-1090 state
the rules this task writes.

- TSK-3510 (not blocking): both write the `route` skill; whichever lands
  second writes the router's outcome rows into it.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The denial rule in the agents and in `meow-author:write`, and the
dispatcher's handling of a `BLOCKED` dispatch beyond its table row, which
TSK-2703 writes. The hand-run cases for a denied `Read`, which TSK-2703 adds.
A check that an agent carries the denial rule, which ADR-1710 leaves to
review. A repository's own agents under `.claude/`, which the outcome rule
doesn't read. The user-facing pages beyond each README's `describes`, which
the document step updates.
