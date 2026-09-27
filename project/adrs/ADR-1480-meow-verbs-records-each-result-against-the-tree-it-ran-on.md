---
id: ADR-1480
artifact: adr
status: approved
revised: 2026-09-27
addresses: [REQ-0146, REQ-0148]
supersedes: []
---

# 1480. `meow-verbs` records each result against the tree it ran on, and evidence cites the record

## Decision

**Amended by ADR-1530.** A result a record cites is kept in the repository,
where anyone can check it; the tree id leaves the evidence directory out; the
ledger is pruned and purged under a lock; and `interrupted` joins the exit
convention as 4.

**Amended by ADR-1560.** Where a submodule has uncommitted changes, the tree
id is `none`, so no edit inside a submodule leaves a result current.

`meow-verbs run` records every verb it runs in a ledger outside the
repository, bound to the tree the verb ran on. A new command,
`meow-verbs evidence`, says for each verb whether its latest result still
holds for the tree as it is now. Evidence cites that record instead of
restating the output (REQ-0146). The `verify` skill calls work done only when
no verb the change needs failed, stayed unresolved or went stale, unless a
person accepts that state (REQ-0148).

Each record carries an identifier of its own, the verb, the command, the
outcome and exit status, the time and the tree id. The whole output goes into
a file beside the ledger, named for the record, because RES-0056 found that
the record keeps everything and only the failing portion enters context. A
verb that stayed unresolved is recorded as unresolved, so the ledger never
reads as if it passed. `run` prints `recorded: <record> at tree <tree id>`
under its summary.

The tree id is git's hash of a tree object. In a git work tree, `meow-verbs`
builds the working state through a temporary index, with untracked files
included and ignored files left out. The id then equals the tree of a commit
that adds every file it counted, and differs from one that leaves an
untracked file out or stages part of a file. `meow-verbs` computes the tree id
before and after each verb. Where the two differ, the verb changed the tree or
someone edited it during the run, and the record is marked as changed during
the run, which `evidence` reports as stale. A formatter that rewrites files
therefore needs a second run, which finds nothing to rewrite and records a
result for the tree it leaves, and the `verify` skill runs `format` before
the other verbs so their results aren't made stale by it. Where the directory
isn't a git work tree, the tree id is `none`, and `evidence` reports the
record as bound to nothing.

The ledger is one file per work tree, at
`<state>/meowpaw/evidence/<key>.jsonl`, with each record's output in
`<state>/meowpaw/evidence/<key>/<record>.log`. `<state>` is
`$XDG_STATE_HOME` where it is set, on every system, and otherwise
`%LOCALAPPDATA%` on Windows and `~/.local/state` elsewhere. The key is a hash
of the work tree's absolute path, so two work trees of one repository keep
separate ledgers. `meow-verbs` only appends to the ledger, one line per record.

`meow-verbs evidence [verb...]` prints the latest record for each named verb,
or for every verb with a record when you name none: the outcome, the record's
identifier and `current`, or `stale` with the tree it ran on and the tree now.
The latest record decides, so a pass after a failure on the same tree reads
as a pass, and going back to a tree that passed earlier reads as stale until
the verb runs again. The command exits as `run` does, so a caller reads one
convention:

- 0 when every named verb's latest record passed on the current tree;
- 1 when one failed or is stale, because in both cases running the verb again
  is the next step, after a fix where it failed, and the line printed says
  which;
- 3 when one has no record, stayed unresolved or is bound to nothing, because
  no run on this tree can produce evidence for it until someone acts: runs it
  for the first time, declares it, or adopts version control.

Evidence names what it closes through the task that cites it, which names the
requirements it closes. The `verify` skill has the model cite a result as
`evidence` prints it: the verb, the outcome, the record and the tree id. It
has the model run `evidence` on the verbs the change needs before calling the
work done. On exit 0 it says the work is done. On anything else it reports
what the command printed and waits for a person to accept it. In a repository
without git, every result is bound to nothing, so the model reports the
command, its exit status and its output as it does today and says the result
is bound to no tree, and a person decides. The method's implement step asks
for the same citation where `meow-verbs` is installed, and for the command,
its exit status and its output where it isn't, because `meow-flow` works
without it.

After this decision a claim that the tests pass names a record you can read
back on the machine that ran it. Its tree id shows whether it is about the
content in front of you, and a reviewer can compare it with the tree of the
branch commit made from that state. What still doesn't work:

- The ledger is per user and per machine, so a record cited in a committed
  task can be read back only there, though anyone can run the verb again on
  the same tree.
- The tree on `main` after a squash merge differs from the branch tree
  whenever `main` has moved, so a record describes the branch, not the merge.
- The check before "done" is an instruction to the model, and no program
  blocks a claim of done.
- An uncommitted edit inside a submodule doesn't change the parent's tree id,
  so a result stays current after it.
- Moving or renaming a work tree leaves its ledger behind under the old key,
  so `evidence` exits 3 until the verbs run again.

## Why

RES-0031 found three properties that make something evidence: a command and
its result, bound to a tree state, naming what it closes. It found that a
model saying "the tests pass" might be recalling a run from twenty edits ago,
in a sentence that reads the same either way. The one mechanism in its survey
that addressed stale evidence bound a revision to each result. Today the
evidence in a task is the output copied by hand, which has the first property
and neither of the others. RES-0056 found that the record of a run is the only
thing anything else may cite as having run a check, and that it keeps the
command, the exit status, the whole output and the tree revision.

RES-0031 recommends adopting that mechanism's revision counter, advanced on
each edit. I bind to content instead. A counter misses an edit made outside the
session and needs a hook in every session, while a tree id changes exactly
when the content does. A tree id also means something after the session ends,
because it can be compared with a commit, and a counter can't. The ledger lives
outside the repository because REQ-0750 keeps recorded evidence and other run
state there, where it costs no diff.

The strongest objection: a record only its own machine can read is no better
than pasted output for anyone else. For them the citation still carries the
tree id, which says whether the result was about the committed content, and
pasted output says nothing about which content it came from.

## Alternatives

| Option                                      | Better at                            | Why it lost                                                                                                                                          |
| ------------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                  | No change                            | REQ-0146 stays unmet, as ADR-1070 left it, and the verify skill's rule V1 holds REQ-0148 by instruction alone, with nothing to find a stale result   |
| A revision counter advanced by an edit hook | No objects written, cheap to compute | Misses edits made outside the session, needs a hook in every session, and means nothing once the session ends                                        |
| The ledger inside the repository            | Readable by every clone              | Every run becomes a diff, against REQ-0750, and results from one machine would read as results for everyone                                          |
| The ledger inside `.git`                    | Removed with the clone               | `.git` sits inside the repository's directory, which REQ-0750 keeps run state out of, and the tree id needs git's object store but not a place in it |
| Hash the files directly, with no git        | Works in a repository without git    | The id would equal no commit's tree, so nobody could compare a result with what was committed                                                        |
| Bind to the commit and a hash of the diff   | Needs no temporary index             | The id changes when the same content is committed, so evidence gathered before a commit no longer matches the commit that recorded it                |

## What it costs

Computing the tree id writes changed and untracked files into the repository's
own `.git` object store as loose objects, twice per verb, which git's
maintenance collects later. A large untracked file is hashed and written on
every run. Each user's state directory grows by one ledger line and one output
file per verb run, and the harness never prunes it. Two sessions appending to
one ledger at once each write a whole line in one write to a file opened for
appending, which keeps lines whole on a local file system and isn't promised on
a network one. `meow-verbs` gains a command, and its skill gains the citation
form and the check before "done".

## What would reverse it

I would move the ledger into the code host's own records if a reviewer asked
for a cited record from another machine and couldn't get it, recorded as a
defect. I would drop the tree id for a cheaper one if computing it added more
than a second to a verb run on a tree of 100,000 files.

## Consequences

- `meow-verbs run` records each verb, keeps its whole output, and prints the
  record and the tree id.
- `meow-verbs evidence` reports whether each verb's latest result holds for
  the current tree.
- The `verify` skill runs `format` first, cites records and checks them before
  the work is called done, and the method's implement step asks for the same
  citation.
- SPC-1040 states the ledger, the tree id and the new command.

## How I will know it was realised

1. Fixtures show `run` writing one record per verb, an unresolved verb
   included, with its whole output, under a state directory the fixture sets,
   outside the repository.
2. Fixtures show `evidence` exiting 0 after a passing run, 1 after a file in
   the tree changes, 1 after a failing run, 1 after a verb that rewrote a
   file, 1 after going back to a tree that passed earlier, and 3 for a verb
   never run.
3. A fixture shows the recorded tree id equal to the tree of a commit that
   adds every file it counted.
4. A fixture shows a directory that isn't a git work tree recorded as bound to
   nothing, and `evidence` exiting 3 for it.
5. The `verify` skill and the implement step carry the order, the citation
   and the check, traced in the task's evidence.
6. Every requirement ADR-1480 addresses lands in exactly one closed task.

## What this does not settle

- Pruning the ledger, which grows until you delete it.
- Running a verb over part of the work (REQ-0140, REQ-0142). When that is
  decided, a record whose command covered part of the work never counts as
  current for the whole verb.
- Where the method's other run state lives, such as the current step and a
  pending approval, which REQ-0750 also covers, and whether REQ-0750's
  "revision counter" should become a requirement naming a tree id.
- Evidence for a helper's output, which REQ-1178 asks for.
