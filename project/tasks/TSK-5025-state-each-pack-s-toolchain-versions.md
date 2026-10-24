---
id: TSK-5025
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-0082, REQ-0085]
issue: 985
projected: ca988f105383
tracked: 59c305d1b63e
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State each pack's toolchain versions and how it prints its tool's configuration

Each pack's README states the versions of its toolchain it is current as of,
and how the pack prints its tool's configuration for the repository to
commit, as SPC-1190 states under "Its tool's configuration and its
versions". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given each of `meow-git`, `meow-github`, `meow-mise`, `meow-gotask` and `meow-markdown`, when a test reads its README, then it carries a line naming each tool it drives and the version it was observed against (REQ-0085). Closed by: a test under `tools/` naming REQ-0085, seen failing first.
2. Given a pack that knows a tool's configuration, when its README is read, then it names the command that prints that configuration, such as `bind`, and says the repository commits what it prints (REQ-0082). Closed by: the same test, naming REQ-0082.

## What to do

Edit each pack's README and add the test under `tools/`, reading the packs
from each unit's `requires.toml` `layer` where TSK-4390 has added it, and
from a list in the test until then. Restamp each page's `describes` as
SPC-1110 states.

## Depends on

- TSK-4390 (not blocking): the `layer` key would let the test find the packs without a list of its own.

## Evidence

Criteria 1 and 2 are closed by `tools/test_pack_readmes.py`, run by the
`test-tools` task: `test_every_pack_readme_states_the_versions_it_is_current_as_of`
for REQ-0085, and
`test_a_pack_that_prints_configuration_says_the_repository_commits_it` for
REQ-0082. Both were seen failing first, on all five READMEs and on the three
that print a stages table. The test reads the five packs the task names from a
list, because the `layer` key it would have read them by also marks the nine
language packs, which state their toolchains in their own words and are left
to a later task. The versions are the ones observed on 2026-10-24: git 2.56.0,
gh 2.101.0, mise 2026.10.7, Task 3.54.0, and the lychee and markdownlint
versions the Markdown pack's skill already named. No unit's version changed,
so no page's `describes` was restamped.

Every stage passed in pull request #PR.

## Left alone

Each pack's skill, which already names the versions the pack was observed
against under SPC-1190.
