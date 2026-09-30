---
id: TSK-4010
artifact: task
status: approved
revised: 2026-09-30
bug: BUG-1380
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Say who opens the one pull request

The method skill says that on the one-pull-request path the session opens
the pull request and names it, or names the branch where the repository
declares no code host. One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/method/SKILL.md`, when its rules are read
   as a list, then M20 says the session opens the pull request and names it
   in its report, and says it names the branch where no code host is
   declared. Closed by: a static test in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the skill, when `meow-checks run check` runs, then the unit stays
   within its `budget.toml`. Closed by: the `budget` check's outcome.
3. Given this change's tree, when `meow-checks run format lint check test`
   runs, then each passes. Closed by: each verb's outcome in the task's pull
   request.

Each criterion is decidable from this task's own work.

## What to do

Change M20, and step 8 where it names the gate, in the method skill, and the
sentence in SPC-1090 that states where the path stops. Add no rule: the
sentence belongs to M20, which already states the stop. Raise `meow-flow`'s
patch version.

## Depends on

- TSK-4000 (not blocking): both raise `meow-flow`'s version, which either
  can write.

## Evidence

`test_the_skill_says_who_opens_the_pull_request` in
`plugins/meow-flow/tests/test_record.py` closes criterion 1. It failed at the
pull request's first commit and passes at its last. The code review found
step 8 naming a pull request where none can exist, M20's new sentence
without its reason and a sentence in the page that misread, and all three
are fixed here. The `budget` check
reports `meow-flow` within its limit, and `meow-checks run format lint check
test` passed all four verbs.

## Left alone

No case measures whether a session opens the pull request, because the
rule is one clause and a run of it needs a code host.
