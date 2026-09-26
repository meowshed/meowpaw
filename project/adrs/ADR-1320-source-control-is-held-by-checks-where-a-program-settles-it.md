---
id: ADR-1320
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-1296,
    REQ-1298,
    REQ-1306,
    REQ-1312,
    REQ-1320,
    REQ-1322,
    REQ-1324,
    REQ-1328,
    REQ-2526,
    REQ-2528,
    REQ-2534,
    REQ-2536,
    REQ-2538,
    REQ-2818,
    REQ-2820,
    REQ-2822,
    REQ-3176,
  ]
supersedes: []
---

# 1320. Source-control discipline is held by a check where a program settles it, and by the commit skill where none does

## Decision

Four parts of how the harness uses source control become checks:

- `meow-scm check-message` reports a `Signed-off-by` trailer that names
  someone other than the commit's author, where the repository requires the
  trailer, because the certificate is a statement the person makes.
- `meow-git push-guard` refuses a push from a branch whose name carries a date
  or the author's name, which the forge already stores.
- `meow-method check frozen` reports a line added to the record that cites a
  commit hash as the revision a check ran at, because the pull request that
  carried a change is the citation that survives a squash.
- Every read of source control in the native tool runs with prompting,
  paging, advice and machine-wide configuration turned off, so a missing
  credential fails where it would otherwise wait.

The rest are rules in `meow-scm`'s `commit` skill, loaded before any commit
message is written: one task maps to one branch, one pull request and one
review, and reaches the trunk as one squashed commit; branches are short-lived
from the one trunk; the harness merges, tags, releases and publishes nothing
without an explicit instruction; one branch is never checked out in two
working trees, which share one repository, and a working tree in use is locked
with a reason; a branch grown past one reviewable change is split; a force
push over a reviewed branch is disclosed. The evidence is recorded for the
signing rules that already hold.

After this decision the parts of source-control discipline a program can see
fail a check, and the rest reach the model before it commits. What still
doesn't work: a version control tool other than git, and invoking work
through a repository's task runner.

## Why

RES-0014 found that one task lands as one branch and one squashed commit, so
the history reads as a list of what the project gained. A squash rebuilds the
commit, so, as REQ-3176 states, a hash a record cites stops resolving on the
trunk, and a sign-off, as REQ-1312 states, is a statement the person makes
that the harness only transcribes. RES-0222 found that a branch name encoding
a date or an author carries what the forge already stores. RES-0131 found a
reading environment with prompting, paging, advice and machine-wide
configuration off, kept apart from the user's own environment for work that
records authorship, and `GIT_TERMINAL_PROMPT=0` turning a hang into a
failure.

Measured at this revision: this repository's verification sections cite the
revision each check ran at as a commit hash, which a squash merge makes
unresolvable on the trunk.

The strongest objection: the hash check reports a hash quoted for another
reason. It reads only a hash in the position of a revision a check ran at,
"at" or "revision" followed by one, and only in lines a change adds, so no
approved record fails for what it already says.

## Alternatives

| Option                                             | Better at                             | Why it lost                                                          |
| -------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------- |
| Checks where a program settles it, rules elsewhere | Each rule held by the strongest means | Chosen                                                               |
| Rules only, in the commit skill                    | Nothing to build                      | The sign-off, the branch name and the hash are all settleable        |
| A hook refusing merges and releases                | Holds every time                      | Can't tell an instructed merge from an uninstructed one              |
| Do nothing                                         | Costs nothing                         | Verification sections keep citing hashes a squash makes unresolvable |

## What it costs

A trailer comparison in `meow-scm`, a branch-name rule in the push guard, a
pattern in the frozen check, one environment for every read, and rules in the
commit skill.

## What would reverse it

- The repository stops squashing, and a commit hash on the trunk survives.

## Consequences

- A sign-off naming someone else, a branch named for a date or its author,
  and a new citation of a commit hash each fail a check.
- The commit skill carries the branching, merging and working-tree rules.

## How I will know it was realised

1. Fixtures show `check-message` refusing a sign-off that names someone other
   than the author, `push-guard` refusing a branch named for a date or its
   author, and `check frozen` reporting an added line citing a hash as a
   revision.
2. A fixture shows each read running with prompting and paging turned off.
3. Each rule ADR-1320 places in the commit skill maps to its requirement in the
   task that closes it.
4. Every requirement ADR-1320 addresses lands in exactly one closed task.

## What this does not settle

- A version control tool other than git.
- Invoking work through a repository's task runner.
