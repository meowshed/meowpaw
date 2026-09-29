---
id: EPC-1651
artifact: epic
status: approved
revised: 2026-09-29
realises: ADR-1710
checked-at:
---

# Every shipped agent reports one of four outcomes, its dispatcher acts on the word, and a denied tool ends it as BLOCKED

Realises exactly one authorising record, ADR-1710. The epic is complete when
each of the three shipped agents ends its report with `outcome:`, a space and one of
`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` and `BLOCKED`, the method skill
and the review step act on that word, a denied tool ends an agent as
`BLOCKED` with nothing waiting, and `meow-author check` fails a unit's agent
that doesn't name all four.

## Acceptance criteria

Taken from ADR-1710, from its list of how I will know it was realised, before
the tasks below were written:

1. Crate tests over fixture agents show `meow-author check` failing, naming
   the file and the word, on a unit agent that names none of the four and on
   one missing only `BLOCKED`, and passing on a unit agent naming all four
   and on a repository agent naming none. The failing fixtures are seen
   failing against the current check before the rule lands.
2. `mise run prompts` and `meow-author check` exit 0 at the merge revision
   with all three shipped agents naming the set.
3. Hand-run evaluation cases, run by a person and never in CI, match
   `^\s*outcome: (DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED)$` on the
   second line of `record-reviewer`'s report on `clean-requirement` and
   `decision-missing-its-reasons`, and on the first line of `prose`'s on
   `decision-without-reason` and of `router`'s on `route-a-tiny-fix`, each in
   at least two runs of three. The same runs show each reviewer's report under
   4,000 characters.
4. A hand-run case under `claude -p --permission-prompts none`, with a deny
   rule on a record's path, starts the method skill's review of that record.
   `record-reviewer` makes exactly one tool call, the denied `Read`, its
   report carries `outcome: BLOCKED` and names `Read` and the path, the
   result's `permission_denials` lists one `Read`, and the gate report calls
   the record unreviewed by an agent.
5. A hand-run case under the same flags starts the review step on a verified
   epic whose change adds a documentation page, with a deny rule on the page's
   path. `prose`'s report carries `outcome: BLOCKED` on its first line and
   names `Read` and the path, `permission_denials` lists one `Read`, and the
   session reports the review of that page as not run.
6. A hand-run case under the same flags starts the method skill's review of a
   record path that doesn't exist. The stream shows exactly two dispatches of
   `record-reviewer`, each report carrying `outcome: NEEDS_CONTEXT`, and the
   gate report calls the record unreviewed by an agent and names the brief it
   sent.
7. A hand-run case under the same flags replaces `record-reviewer` with a
   repository agent whose definition says nothing of an outcome, and starts
   the method skill's review of a record. The agent's report holds no line
   matching the pattern in criterion 3, and the gate report calls the record
   unreviewed by an agent.
8. Every requirement ADR-1710 addresses, REQ-0816 and REQ-2978, lands in
   exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [ ] T-001 TSK-2702 give the three shipped agents the outcome line, the
      cause line and, for the two reviewers, the quoting rule; make
      `meow-author check` in `crates/meow/src/author.rs` require the four
      words; make the method skill and the review step's W13 act on each
      outcome; add the outcome graders and the hand-run cases for criteria 6
      and 7
      closes: REQ-0816
      depends: nothing

- [ ] T-002 TSK-2703 give the three shipped agents and `meow-author:write` the
      denial rule, make the method skill and W13 end a `BLOCKED` dispatch
      without resuming, re-sending or reviewing it themselves, report
      `prose`'s unreadable standard as `BLOCKED`, and add the hand-run cases
      for criteria 4 and 5
      closes: REQ-2978
      depends: TSK-2702 (blocking) - the denial rule ends the agent with
      `outcome: BLOCKED`, a line only TSK-2702 makes the agents write and the
      dispatchers read

The two tasks run in order, because TSK-2703 writes into the same three
agents and the same two skill files, and its rule ends on a word TSK-2702
defines.

## Coverage

ADR-1710 addresses two requirements, and each lands in one task. REQ-0816
lands in TSK-2702, because the fixed set, the line that carries it, the short
report and the dispatcher that acts on the word without reading the rest are
that requirement. REQ-2978 lands in TSK-2703, because the denial rule and the
dispatcher's refusal to resume, re-send or go round a `BLOCKED` dispatch are
what make a dispatch expect the denial.

Criteria 1, 2, 3, 6 and 7 close in TSK-2702, and criteria 4 and 5 in TSK-2703.
Criterion 8 is checked at the verify step by `paw check coverage`.

The smallest set that tests the decision is TSK-2702: with it, every shipped
agent writes a line a dispatcher reads without parsing prose, and the gate
fails a unit agent that drops a word. Before either task is finished, one
thing can be measured: the number of shipped agents whose definition names all
four outcomes, which is 0 today and must be 3.

Criteria 3 to 7 rest on how a model follows its definition and on the
platform's `permission_denials`, which a third party controls. The project
ships the definitions, the dispatcher rules and the hand-run cases, and a
person runs the cases and keeps what they print.

Open question, blocking nothing: the `route` skill ADR-2100 decided, which
TSK-3510 adds, hasn't landed at this epic's revision. SPC-1090 states the
router's outcome rows under "The route", so whichever of TSK-3510 and
TSK-2702 lands second writes them into the skill, as ADR-1710 says. If
TSK-2702 lands first, its evidence says so, and the router's outcome line is
read only by a person until the skill ships.

## Not covered

- What the four outcomes mean for an agent that implements work, which the
  decision that ships one settles.
- A check of an agent's outcome against `permission_denials`, which waits for
  a program that runs the harness unattended.
- A check that a unit's agent carries the denial rule, which ADR-1710 leaves
  to review, because a pattern for a sentence either misses a paraphrase or
  passes a near miss.
- A permission prompt a background agent leaves waiting in an interactive
  session, which ADR-1710 reads as outside REQ-2978.
- The user-facing pages beyond each unit's README `describes`, which the
  document step updates from ADR-1710's consequences once both tasks are
  done.
