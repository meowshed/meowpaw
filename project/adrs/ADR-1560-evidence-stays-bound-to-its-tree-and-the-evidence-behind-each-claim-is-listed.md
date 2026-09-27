---
id: ADR-1560
artifact: adr
status: approved
revised: 2026-09-27
addresses: [REQ-0452, REQ-0454, REQ-0456]
supersedes: []
---

# 1560. Evidence stays bound to its tree, and the evidence behind each claim is listed

## Decision

This decision amends ADR-1480 in one place, the tree id of a work tree with a
dirty submodule, and adds a listing to `meow-verbs evidence`; the rest of
ADR-1480 holds.

Evidence records the tree it was collected at through the tree id ADR-1480
added to every record and ADR-1530 copied into every kept file (REQ-0452). Any
change to the tree, a tracked file, an untracked file or a staged one, gives a
new tree id, so a record collected before it reads as stale and can't be kept
(REQ-0454). One change escaped the tree id: an uncommitted edit inside a
submodule, which ADR-1480 names as a gap, since the parent's tree records only
the submodule's commit. Where a submodule has uncommitted changes, counted the
way the parent counts them, untracked files included and ignored ones left
out, the tree id is `none`. A result collected then is bound to nothing, and a
result collected earlier, compared with a tree id that is now `none`, reads as
bound to nothing too; `evidence` names the dirty submodule as the reason and
exits 3, so no edit in a submodule leaves an earlier result current. Apart
from that, the decision takes REQ-0452 and REQ-0454 as ADR-1480 met them, and
the task that closes them traces the fixtures that already hold them.

`meow-verbs evidence --kept` lists the evidence behind the claims of the
current work (REQ-0456). It lists every file in the evidence directory that
this work adds against the branch's base on the trunk the profile declares as
`trunk` under `[git]`: files committed on the branch, uncommitted ones and
untracked ones alike. For each it prints the record identifier, the verb, the
outcome and the tree id, and whether that tree id equals the tree of `HEAD`
less the evidence directory. The record identifier is what a task's Evidence
section cites, so it joins each claim to its line. Only the latest kept file
per verb counts; an earlier one is listed as `superseded`, because a branch
that keeps a result and then changes its code keeps a new one, and the old
file may still be cited by a task written before. The comparison is with
`HEAD`, not the working state, because a change's claims are about what it
commits; run before the commit, a fresh result reads as differing until the
work is committed.

The listing exits as `evidence` does, weighing each counted file's outcome
and match: 1 where one failed or differs from `HEAD`; else 4 where one was
interrupted; else 3 where the listing is empty, couldn't tell which files
belong to this work, or found one bound to nothing; else 0. Where no trunk is
declared, or the branch has no base on it, the listing covers every kept file
and says it couldn't tell which belong to this work. Outside a git work tree
every kept file is listed as bound to nothing.

After this decision the harness can answer, for the claims in a change, which
kept results back them and whether each still describes the change. What still
doesn't work: a claim made in prose with no kept result behind it isn't
listed, because the listing starts from the evidence and not from the claims,
and what keeps such claims from being made is the `verify` skill's
instruction, which no program enforces. A repository whose submodule is
always dirty, such as one built inside the submodule or a vendored one its
author can't commit to, can never keep evidence while that holds.

## Why

RES-0031 found three properties that make something evidence: a command and
its result, bound to a tree state, and naming what it closes; and that the one
mechanism in its survey addressing stale evidence bound a revision to each
result, so evidence collected before a change can't satisfy completion. The
tree id is that binding, and ADR-1480 chose it because it changes exactly when
the content does, so REQ-0452 and REQ-0454 need nothing new.

RES-0031 also found that evidence attached to nothing accumulates without
being checkable. A kept file names its record, and the task that cites it
names the requirements it closes, so listing what a change keeps, against the
tree it holds, is the report REQ-0456 asks for.

The strongest objection: listing evidence doesn't find a claim with no
evidence. It doesn't. The `verify` skill and the implement step tell the model
not to make one, as an instruction ADR-1480 says no program enforces, and the
listing can't detect a breach of it. I count REQ-0456 closed with that limit
named, because it asks the harness to report the evidence behind a claim, and
every claim made as the method asks cites a record the listing reports.

## Alternatives

| Option                                                  | Better at                                                                   | Why it lost                                                                                                                                                    |
| ------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                              | No change                                                                   | REQ-0452 and REQ-0454 stay closed by no task although they hold except for the submodule gap, which stays open, and nothing lists the evidence behind a change |
| Parse each task's Evidence section for claims           | Starts from the claims                                                      | Reads prose as data, and a sentence phrased another way would drop out of the report unnoticed                                                                 |
| List every kept file in the repository                  | Needs no trunk                                                              | The evidence of every past change buries the few files the current work adds                                                                                   |
| Match the record identifiers tasks cite                 | Finds a cited record with no kept file, where prose phrasing doesn't matter | Only `meow-flow` knows where the record's tasks live and which are this work's, so the match belongs in `paw`, which this decision leaves for later            |
| Hash a dirty submodule's working state into the tree id | A result can still be kept while a submodule is dirty                       | The id would no longer be a git tree id, so `meow-verbs tree` couldn't compare a kept record with the commit that carries it                                   |

## What it costs

`meow-verbs` gains one flag, and it reads the trunk from `trunk` under the
profile's `[git]` table, which `meow-git` also reads; whoever changes what that
key means in either unit has to change the other, and a repository that
declares a trunk for `meow-git` gets it used here too. Each listing costs one
`git diff` against the base and one listing of untracked files, paid by whoever
runs it. A result collected with a dirty submodule can't be kept, so its author
commits the submodule first; a repository whose submodule is always dirty can't
keep evidence at all, and pays for that until it ignores the submodule's build
output or commits to it.

## What would reverse it

I would start the listing from the claims if tasks came to carry their
evidence as structured fields, because then a claim with no kept result could
be found without reading prose. I would hash a dirty submodule into the tree
id, and give up comparing it with a commit, if a defect recorded that a
repository couldn't keep evidence because of its submodule.

## Consequences

- `meow-verbs evidence --kept` lists the kept files a change adds, each with
  whether it still describes the change.
- ADR-1480 carries a line naming this amendment.
- SPC-1040 states the listing, the dirty submodule and the existing mechanism
  holding REQ-0452 and REQ-0454.

## How I will know it was realised

1. The task's evidence traces the `Ledger` and `Kept` fixtures that show a
   record's tree id and a stale record after any change. Fixtures show a
   result collected with a dirty submodule bound to nothing, and a result
   collected on a clean tree reading as bound to nothing, naming the
   submodule and exiting 3, once a submodule file is edited (REQ-0452,
   REQ-0454).
2. Fixtures show `evidence --kept` listing only the files a branch adds,
   committed or not, each with its record identifier and whether it matches
   `HEAD`; a superseded file listed and not counted; a failed result exiting
   1; an empty listing exiting 3; every kept file listed with a note where no
   trunk is declared; each marked bound to nothing outside git; and a record
   identifier a task cites found in the listing (REQ-0456).
3. Every requirement ADR-1560 addresses lands in exactly one closed task.

## What this does not settle

- Finding a claim made with no evidence behind it, and matching the record
  identifiers tasks cite, which belongs in `paw`.
- Whether a claim made without evidence breaks the method, which stays an
  instruction to the model.
