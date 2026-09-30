---
id: TSK-3130
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1800
closes: [REQ-0083]
issue: 637
projected: 3aa190635dfe
---

# Write the Markdown skill and `reviewing.md`

The skill tells the model what ADR-1900 orders it to, in RES-0111's order, and
`reviewing.md` carries the six points a Markdown reviewer checks that no
command reports, loaded when Markdown is reviewed, as SPC-1195 states. One
task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `reviewing.md`, when a test reads it, then it finds each of RES-0111's
   six reviewer points: the heading outline as the argument, a table against a
   list, the language tag on a fence, reference links for a source cited more
   than twice, links that survive a move, and a diagram claiming what the
   prose doesn't. Closed by: a fixture naming REQ-0083, seen failing first.
2. Given the skill, when a test reads it, then it names `reviewing.md` as the
   file to load on review, forbids markdownlint-cli against a
   `.markdownlint-cli2.*` file, failing a check on an unreachable link without
   saying so, and a spell check with no project word list, names `meow-prose`
   as the owner of the writing standard, and names the tool versions from
   RES-0294. Closed by: a fixture.
3. Given the skill, when `mise run prompts` and `mise run budget` run, then
   both pass, and the skill's per-turn load stays within the unit's
   `budget.toml`. Closed by: the gate, exit status 0.
4. Given the skill's order and wording, when a reviewer reads it against
   RES-0111's order, then it follows that order. Closed by: judgement, by the
   pull request's reviewer, because the order of a prompt's sections is read,
   not matched.

## What to do

Write the skill's body and `reviewing.md` under
`plugins/meow-markdown/skills/markdown/`, to the prompt vocabulary
`meow-author:write` sets, carrying what the skill knows of front matter,
admonitions and diagram blocks for the seven known render targets. Raise
`meow-markdown`'s minor version.

## Depends on

TSK-3100, because the unit and its skill file come from it.

## Evidence

The cover commit 4142a15 added seven checks to
`plugins/meow-markdown/tests/test_markdown.py`, and they failed there before
the work, as `project/evidence/cfe2a8d9882c.txt` records. With the skill and
`reviewing.md` written, the same checks pass unchanged:

```text
$ python3 -m unittest plugins/meow-markdown/tests/test_markdown.py -k Reviewing -k Skill
Ran 7 tests in 0.002s
OK
exit status 0
```

The unit's whole test file passes, with one test skipped because lychee isn't
installed on this machine, so TSK-3120's real lychee run couldn't be made:

```text
$ python3 -m unittest plugins/meow-markdown/tests/test_markdown.py
Ran 47 tests in 5.529s
OK (skipped=1)
exit status 0
```

`git diff 4142a15 -- plugins/meow-markdown/tests/test_markdown.py` printed
nothing, so the checks are the ones the cover commit holds. Criterion 3:
`mise run prompts` printed `53 files, 0 authoring failures` and `mise run
budget` printed `meow-markdown: 326 of 380 characters on every turn`, both
exit status 0. Criterion 4 waits on the pull request's reviewer.

The render-target table in `SKILL.md` comes from the renderers' documentation
as I know it, not from an observation the pack made, and the skill says so and
tells the model to check the renderer's configuration before reporting a
finding on it. `meow-markdown` rises to 0.4.0, a minor, because the skill
gained a capability.

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

The program's commands, which TSK-3100, TSK-3110 and TSK-3120 take. The
writing standard, which stays in `meow-prose`.
