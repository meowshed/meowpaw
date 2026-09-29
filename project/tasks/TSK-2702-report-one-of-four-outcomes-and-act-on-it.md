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

- Checks: crates/meow/src/author.rs plugins/meow-author/tests/test_author.py tools/test_shipped_agents.py plugins/meow-flow/tests/test_record.py plugins/meow-prose/tests/test_prose_agent.py
- Failing run: project/evidence/b7fd3db95397.txt project/evidence/d3979c5f92d6.txt project/evidence/042104530e84.txt project/evidence/d481010ed6f9.txt project/evidence/0fb448bbe505.txt
- Landed in: #734
- Judgement: 6: the graders run a model by hand and never in CI, so a person reads the kept transcripts; 7: a person runs the hand-run case and reads the kept stream; 8: a person runs the hand-run case and reads the kept stream; 9: the kept run of `format lint check test build` at implement closes it

Criterion 1 is covered twice. The crate tests in `author.rs`,
`a_unit_agent_naming_no_outcome_fails`,
`a_unit_agent_missing_only_blocked_fails`,
`a_unit_agent_naming_all_four_passes` and
`a_repository_agent_naming_no_outcome_passes`, hold the exit status. They
can't read what the check prints, so the class `AgentOutcomes` in
`test_author.py` runs the built launcher and requires the failure lines to
name the file and exactly the missing words, including a fixture missing only
`DONE`, because `DONE_WITH_CONCERNS` mustn't count as naming it. The
`agent()` fixture there now names the four outcomes by default, so the field
fixtures in `AgentFields` keep failing on their field alone once the rule
lands.

Criterion 2 is covered by `ShippedOutcomes` in `tools/test_shipped_agents.py`,
which requires the three shipped agents to name the four outcomes and
`meow-author check` to exit 0 over the units. The `prompts` task in the `lint`
verb runs the same check at implement.

Criterion 3 is covered by `AgentReports` in `test_record.py` for
`record-reviewer` and `router`, and by `ProseReport` in the new
`plugins/meow-prose/tests/test_prose_agent.py` for `prose`. The profile's
`test` verb now runs that directory. `ProseReport`'s quoting check passes
already, because V1 holds the rule, and it guards the rule through the
rewrite. Criterion 4 is covered by
`MethodSkill.test_the_skill_acts_on_the_reviewers_outcome` and criterion 5 by
`MethodSkill.test_the_review_step_dispatches_the_two_reviewers`, both in
`test_record.py`.

The `test` verb stops at the first suite that fails, so five runs are kept,
each from a tree that sets aside the checks of the suites before it:
`b7fd3db95397.txt` holds every check, and the two crate tests that expect a
failure fail; `d3979c5f92d6.txt` sets aside the crate tests, and
`meow-flow` reports 20 failures; `042104530e84.txt` also sets aside
`test_record.py`, and `meow-author` reports 4; `d481010ed6f9.txt` also sets
aside `test_author.py`, and `meow-prose` reports 6; `0fb448bbe505.txt` also
sets aside `test_prose_agent.py` and its line in the profile, and
`test_shipped_agents.py` reports 3. Every check that passed in those runs is a
fixture expected to pass, beside a failing one in the same class.

## Evidence

Done. Closes REQ-0816.

The checks failed first: the cover commit 5bb523ac, rebased as 5c7a2309 onto
main, kept the five failing runs the Cover names, one for each suite that
stopped on a failing check.

`cargo test --all-features -- author::`, from `crates/meow`, exited 0 and
printed `7 passed; 0 failed`, the four outcome tests among them.
`python3 -m unittest discover -s plugins/meow-author/tests` exited 0 and
printed `Ran 51 tests` and `OK`. `python3 -m unittest test_record`, from
`plugins/meow-flow/tests`, exited 0 and printed `Ran 227 tests` and `OK`.
`python3 -m unittest discover -s plugins/meow-prose/tests` exited 0 and
printed `Ran 4 tests` and `OK`. `python3 -m unittest
tools/test_shipped_agents.py` exited 0 and printed `Ran 6 tests` and `OK`.
`plugins/meow-author/bin/meow-author check` exited 0 and printed
`53 files, 0 authoring failures`.

`git diff 5bb523ac745c2eecbd735e55334833548fe58d10 --` over the five check
files printed only the check's own code in `crates/meow/src/author.rs`, and
nothing in any test, so the checks are as the cover wrote them.

TSK-3510 landed `plugins/meow-flow/skills/route/SKILL.md` first, in #722, so
this change writes the router's outcome rows from SPC-1090 "The route" into
it, as R10, and step 3 reads `outcome:` before the other fields.

The Cover's Judgement line named criteria 7 and 8 as one entry, which
`paw ready implement` read as a criterion named `7 and 8`; this change splits
it into one entry for each, with the same reason.

Criteria 6, 7 and 8 rest on judgement: the outcome and length graders, and the
hand-run cases `review-a-missing-path` and `reviewer-with-no-outcome`, are
added, and no model ran them in this change.

The five verbs' run is kept under `project/evidence/` in this change.

## Left alone

The denial rule in the agents and in `meow-author:write`, and the
dispatcher's handling of a `BLOCKED` dispatch beyond its table row, which
TSK-2703 writes. The hand-run cases for a denied `Read`, which TSK-2703 adds.
A check that an agent carries the denial rule, which ADR-1710 leaves to
review. A repository's own agents under `.claude/`, which the outcome rule
doesn't read. The user-facing pages beyond each README's `describes`, which
the document step updates.
