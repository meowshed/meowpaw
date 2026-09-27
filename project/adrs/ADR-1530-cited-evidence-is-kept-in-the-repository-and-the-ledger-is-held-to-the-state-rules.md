---
id: ADR-1530
artifact: adr
status: approved
revised: 2026-09-27
addresses:
  [
    REQ-0752,
    REQ-0754,
    REQ-0756,
    REQ-0758,
    REQ-2956,
    REQ-2958,
    REQ-2960,
    REQ-2962,
    REQ-2964,
    REQ-2966,
    REQ-2967,
    REQ-2968,
    REQ-2969,
    REQ-2970,
    REQ-3072,
  ]
supersedes: []
---

# 1530. Cited evidence is kept in the repository, and the ledger is held to the state rules

## Decision

This decision amends ADR-1480 in four places, and the rest of ADR-1480 holds:

- a result a record cites is copied into the repository, where anyone can
  check it, and the ledger outside it stays run state, the harness's own log
  of what it ran (REQ-2956, REQ-3072);
- the tree id leaves the evidence directory out, so it equals a commit's tree
  only through `meow-verbs tree`;
- the ledger is pruned and purged under a lock, where ADR-1480 only appended
  to it and never pruned it;
- a fourth outcome, `interrupted`, joins the exit convention as 4.

`meow-verbs evidence --keep [verb...]` writes each named verb's latest record,
where it is current, into the repository, one file per record at
`.meowpaw/evidence/<record>.log`. A repository can move the directory with
`evidence_dir` under `[verbs]`, so a repository with a layout of its own
chooses where evidence lives; moving it means keeping the records again,
because the old directory then counts in the tree id. Each file opens with a
header naming its format, `meow-verbs evidence 1`, then the verb, the command,
the targets, the outcome, the exit status, the tree id and the time, and holds
the whole output after it. The format is a contract, numbered so a later
change is visible, because a person reading the repository relies on it
(REQ-2964). A task cites the kept file's path beside the record. A record that
isn't current can't be kept, because it describes other content than the
tree. `--keep` with no verb named keeps every verb whose latest record is
current, as `evidence` with none reads every verb with a record, and names
each file it wrote. A kept file holds whatever the verb printed, secrets
included, so the person who keeps it reads it before committing it, and the
`verify` skill has the model check the file for secret material first.

The tree id leaves the evidence directory out, wherever `evidence_dir` puts
it, because the evidence describes the work and is not part of it; otherwise
keeping a record would change the tree it names. `meow-verbs tree <commit>`
prints a commit's tree id with that directory left out, the id a reviewer
compares with a kept record's.

The ledger outside the repository is run state, and holds to the rules
RES-0262 found for run state:

- It is keyed by the work tree's absolute path, as ADR-1480 decided, and each
  record names the repository's identity, the hash of its first commit,
  inside it, so state can be found either way (REQ-0752).
- A missing ledger or a line that doesn't parse, such as a last line cut
  short while another session writes it, is reported as absent, never as a
  result (REQ-0754).
- `meow-verbs state` prints where the ledger is, how many records it holds,
  the oldest and newest, and the evidence directory, in words a person reads
  (REQ-0756). `evidence` already prints the records.
- Every write to the ledger takes a lock (REQ-2967), a file in the platform's
  runtime directory: `$XDG_RUNTIME_DIR` where it is set, and otherwise the
  user's own temporary directory, which the system cleans (REQ-2958). An
  append waits for the lock, which is held for one rewrite of one file, so no
  session's line is lost to another's prune (REQ-0758). A lock older than a
  minute is taken as a dead process's and replaced, because a rewrite takes
  well under that.
- `MEOWPAW_STATE_DIR` moves the state directory, and `MEOWPAW_STATE=off`
  stops every write outside the repository, with `run` saying each result was
  not recorded (REQ-2960).
- The first `run` that finds a record older than 30 days drops every such
  record and its output file, because a record that old names a tree the work
  has long left, and `meow-verbs state --purge` drops them all (REQ-2962). A
  `run` that finds the lock held skips the prune and leaves it to the next run,
  so no verb waits on it. The 30 days are fixed, because nothing reads a
  record for longer.
- A prune or a purge writes the ledger it keeps to a temporary file and
  renames it into place, and `--keep` writes each evidence file the same way.
  An append adds one whole line under the lock, and a reader skips a line cut
  short, so a reader sees one version or the other (REQ-2966).
- The ledger's format is private: nothing but `meow-verbs` reads it, and the
  kept file is the contract others read (REQ-2964).

`run` records a verb as started before it runs it, in a line naming the
record, its process id, the process's start time and the host, and appends a
second line naming the same record when the verb ends; `evidence` pairs the
two by the record's identifier. A record with a start and no end reads as
`running` while a process with that id and start time lives on this host, and
as `interrupted` otherwise (REQ-2968). A verb whose process ends on an
interrupt or a termination signal is recorded as `interrupted` too, a fourth
outcome beside passed, failed and unresolved, because it says the run stopped
and nothing about the work (REQ-2969). `run` and `evidence` share one
convention, as ADR-1480 decided: 1 where a verb failed, or for `evidence` went
stale; else 4 where one was interrupted or, for `evidence`, is still running;
else 3 where one was unresolved; else 0. An interrupted verb outranks an
unresolved one, because it is the one the next run can fix. Nothing is retried
on its own, because a retry could hide a failure behind a later pass.

`evidence` reports the current work tree by default, and `evidence --all`
adds every other work tree whose records name the same repository, each
labelled with its path (REQ-2970).

After this decision a task's evidence can be read on any machine, a ledger
holds only what one machine needs, and a run cut short says so. What still
doesn't work: kept evidence grows the repository with every result a record
cites; a repository with `MEOWPAW_STATE=off` can keep nothing, because `run`
records nothing to keep; secret material in a kept file is caught only by the
person keeping it; and a lock left by a dead process holds a prune back for up
to a minute.

## Why

RES-0262 found that everything a second person needs to trust the work
belongs in the repository, and that evidence living on one machine is an
assertion, however large it is. REQ-0750 had counted recorded evidence as run
state, and REQ-2956 keeps it in the repository; the owner chose the
repository on 2026-09-27, REQ-3072 replaced REQ-0750, and this decision follows
it. The ledger ADR-1480 built is the right place for a machine's log of what
it ran, and the wrong place for what a record cites.

RES-0262 also found the state rules this decision adopts: keyed by work tree
path with the repository's identity inside, relocatable and suppressible,
bounded, written atomically, locked for a read-modify-write with the lock in
the runtime directory, a format either promised or private, a step recorded
as started and reported as interrupted, a fourth outcome, and aggregation
offered, never assumed.

Keeping only what a record cites, and not every run, keeps the repository's
growth to the evidence someone relies on.

The strongest objection: test output committed to a repository grows it
without end and fills its diffs. It does, by the results people cite, and
RES-0262 weighed exactly this case and found the alternative is evidence
nobody else can check.

## Alternatives

| Option                                        | Better at                           | Why it lost                                                                                   |
| --------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------- |
| Keep everything outside, as ADR-1480 did      | The repository doesn't grow         | Evidence on one machine is an assertion, against REQ-2956, and the owner chose the repository |
| Keep a summary inside and the output outside  | Small files                         | The output is what a reviewer checks, and REQ-2956 keeps evidence inside however large        |
| Keep every run's record inside                | No step to choose what to keep      | Most runs are iterations nobody cites, and the repository would grow with each                |
| Include the evidence directory in the tree id | The recorded id equals the commit's | Keeping a record would change the tree it names, so kept evidence could never be current      |

## What it costs

Each cited result adds a file to the repository, paid in size by everyone who
clones it, and in reading by every reviewer of a pull request that cites
evidence, unless the repository marks the directory as generated for its code
host. The person who keeps a file carries the risk of secret material in it.
`meow-verbs` gains `evidence --keep`, `evidence --all`, `state`,
`state --purge` and `tree`, a fourth outcome and an exit status of 4, which
whoever maintains a CI step or hook reading that status has to handle where it
treats anything but 0, 1 and 3 as a crash. A reviewer comparing a kept tree id
with a commit uses `meow-verbs tree`, one step more than ADR-1480's
comparison.

## What would reverse it

I would move kept evidence out of the main history, into a separate branch or
the code host's own storage, if kept files came to be most of a repository's
size, measured on this repository, because then cloning pays mostly for
evidence. The fourth outcome, the exit status and the lock's place follow
from requirements, and change only with them.

## Consequences

- ADR-1480 carries a line naming this amendment and its four changes.
- `meow-verbs` keeps cited records in the repository, records the
  repository's identity and the interrupted outcome, prunes, purges, locks,
  prints its state and aggregates across work trees on request.
- The `verify` skill and the implement step cite a kept record's path.
- SPC-1040 states the kept file's format, the state rules and the new
  outcome.

## How I will know it was realised

1. Fixtures show `evidence --keep` writing a current record's file with its
   header and whole output, refusing a stale record, and leaving the tree id
   unchanged; and a changed `evidence_dir` used.
2. Fixtures show the repository's identity in each record; a corrupt line
   reported as absent; a started record reported as running while its process
   lives and interrupted after; a verb killed by a signal recorded as
   interrupted, with exit 4 from `run` and `evidence`; records older than 30
   days dropped by a run under the lock; `state --purge` emptying the ledger;
   a stale lock replaced; an append made during a prune kept; a dropped
   record's output file deleted; `MEOWPAW_STATE=off` writing nothing;
   `MEOWPAW_STATE_DIR` moving it; `state` printing the ledger's facts;
   `tree <commit>` matching a kept record's tree id; bare `--keep` keeping
   every current verb; and `evidence --all` listing a second work tree's
   records.
3. The `verify` skill and the implement step cite the kept path, traced in the
   task's evidence.
4. Every requirement ADR-1530 addresses lands in exactly one closed task.

## What this does not settle

- Keeping evidence outside the main history, which its reversal names.
- The method's own run state, such as the current step, which REQ-3072 covers
  once the method keeps any.

## Open review findings

- Leaving the kept file's field list and the environment variables to
  SPC-1040. Left: the field list is the contract a person reads, which this
  decision chooses, and SPC-1040 restates it for the program.
