---
id: TSK-5025
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-0082, REQ-0085]
issue:
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

Not yet.

## Left alone

Each pack's skill, which already names the versions the pack was observed
against under SPC-1190.
