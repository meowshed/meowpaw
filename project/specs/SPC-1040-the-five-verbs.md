---
id: SPC-1040
artifact: spec
status: live
revised: 2026-09-27
checked-at: "#115"
states:
  [
    REQ-0130,
    REQ-0131,
    REQ-0134,
    REQ-0135,
    REQ-0136,
    REQ-0140,
    REQ-0142,
    REQ-0144,
    REQ-0146,
    REQ-0148,
    REQ-0150,
    REQ-0154,
    REQ-0156,
    REQ-0158,
    REQ-0452,
    REQ-0454,
    REQ-0456,
    REQ-0752,
    REQ-0754,
    REQ-0756,
    REQ-0758,
    REQ-2908,
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
---

# The five verbs

## Scope

This covers the five verification verbs a repository declares and the unit
that resolves, reports and runs them, `meow-verbs`. It states where a verb
resolves from, what an unresolved verb reports, and what a run records.

It leaves binding a verb to a runner's tasks and language packs to later
decisions, which ADR-1070 names. How the
unit's skill is written is SPC-1030's.

ADR-1070, ADR-1480, ADR-1520, ADR-1530, ADR-1550 and ADR-1560 decide it,
EPC-1040, EPC-1460, EPC-1500, EPC-1510, EPC-1520 and EPC-1530 realise them,
and
`meow-verbs` implements it, checked at #115.

## Boundary

| Surface                             | What it is                                                      |
| ----------------------------------- | --------------------------------------------------------------- |
| `.meowpaw/profile.toml`, `[verbs]`  | The repository's declaration: one command per verb it declares  |
| `plugins/meow-verbs/bin/meow-verbs` | The program: `status`, `run <verb>...` and `evidence [verb...]` |
| `<state>/meowpaw/evidence/`         | The ledger of recorded results, outside the repository          |
| `plugins/meow-verbs/skills/verify/` | The skill that tells the model to use the program, not a guess  |
| `plugins/meow-verbs/README.md`      | The unit's documentation page                                   |

## Behaviour

### The verbs

There are five verbs and no others: `format` for formatting, `lint` for static
analysis, `check` for type checking, which in a compiled language is the
compiler checking the code without building it, `test` for tests and `build`
for the build (REQ-0130, REQ-2908). A unit adds no sixth (REQ-0131), because a
sixth verb is a command with no agreed meaning across repositories.

From `meow-verbs` 0.4.0 the program no longer reads the names the verbs had
before ADR-1410, `fmt` for `format` and `typecheck` for `check`: a profile key
under an old name is listed as ignored, and an old name on the command line
isn't a verb.

### Where a verb resolves from

A verb resolves from the command the repository declares for it, and from
nowhere else (REQ-0134):

```toml
[verbs]
format = "mise run fmt-check"
lint = "mise run lint"
```

The value is one command, run by the shell from the repository's root, or a
table whose `command` is that command and whose optional `subset` runs the
verb over part of the work, with `{targets}` where the part goes:

```toml
[verbs.test]
command = "./scripts/test"
subset = "./scripts/test {targets}"
```

`run <verb>... -- <target>...` runs each named verb through its `subset`, with
every `{targets}` replaced by the targets, each quoted for the shell and
separated by spaces (REQ-0140). A verb with no `subset` is unresolved of the
kind `no subset form` and doesn't run, and the program never runs the whole
command in its place (REQ-0142). A `subset` without `{targets}` is a
`malformed declaration`, and a `--` naming no target is a usage error
(ADR-1520). The
unit never guesses a command and never substitutes one it found another way
(REQ-0158), because a guessed command produces a green report with nothing
behind it.

The profile is read from the repository's root only, found as the top of the
version control working tree the program runs in, or the current directory
where there is none. It doesn't walk further up, because a repository has one
answer to what a verb means.

### What `status` reports

`meow-verbs status` reports all five verbs and runs none of them (REQ-0150).
For a resolved verb it gives the command and the file it came from. For an
unresolved verb it gives the kind, one of five, and a run over part of the
work adds a sixth (REQ-0154, REQ-0142):

| Kind                  | Means                                                                    |
| --------------------- | ------------------------------------------------------------------------ |
| undeclared            | The profile exists and doesn't name the verb                             |
| no profile            | The repository has no `.meowpaw/profile.toml`                            |
| profile unparseable   | The profile exists and can't be read; the parser's message is shown      |
| malformed declaration | The profile names the verb with a value that isn't one command           |
| no interpreter        | The program can't run on this machine: the unit carries no binary for it |
| no subset form        | A run over part of the work names a verb that declares no `subset`       |

A key under `[verbs]` that is not one of the five, and a table the unit
doesn't read, are listed as ignored, so the person learns why a setting had no
effect. An unparseable profile resolves no verb, and nothing falls back.

`status --json` gives the same report as one JSON object, for a program to
read.

### What `run` reports

`meow-verbs run <verb>...` runs each named verb in the order given and reports
each one (REQ-0144, REQ-0156):

- a verb that ran: the exact command, its exit status, how long it took, and
  its whole output, standard output and standard error in the order they
  arrived
- a verb that failed: the same, led by the last lines of its output, where a
  failing tool almost always puts its error (REQ-0135)
- an unresolved verb: its kind, and the words "not run"

An unresolved verb is never reported as passed (REQ-0136). The program ends
with a summary line naming each verb as passed, failed or unresolved, and
exits with 0 only when every named verb ran and passed: 1 when any failed, and
3 when none failed and any was unresolved. `run` with no verb named is an
error, because a run of every declared verb would pass while the undeclared
ones went unmentioned.

### What `run` records

`run` records each verb it runs, an unresolved one included, in a ledger
outside the repository: the verb, the command, the outcome, the exit status,
the time and the tree id, with the whole output in a file named for the
record. Under its summary it prints one line per verb:
`recorded: <verb> <record> at tree <tree id>`
(REQ-0146) (ADR-1480). The ledger is `<state>/meowpaw/evidence/<key>.jsonl`,
where `<state>` is `$XDG_STATE_HOME` where it is set, and otherwise
`%LOCALAPPDATA%` on Windows and `~/.local/state` elsewhere, and `<key>` is a
hash of the work tree's absolute path. `meow-verbs` only appends to it.

The tree id is git's hash of the working state as a tree object, untracked
files included and ignored ones left out, built through a temporary index so
the repository's own index is untouched. It equals the tree of a commit that
adds every file it counted. The program takes it before and after each verb,
and a record whose two ids differ is marked as changed during the run. Outside
a git work tree the tree id is `none`.

### What `evidence` reports

`meow-verbs evidence [verb...]` prints the latest record for each named verb,
or every verb with a record when none is named: its outcome, its identifier,
and `current` or `stale` with the tree it ran on and the tree now. The latest
record decides. It exits 0 when every named verb's latest record passed on the
current tree; 1 when one failed, is stale or changed during its run; and 3
when one has no record, was unresolved or is bound to no tree (REQ-0148).

A record from a subset run carries its targets, and `evidence` never counts it
as current for the whole verb: it reads the latest record run without
targets, prints the latest subset record beside it as `subset only`, and reads
a record carrying no targets field as a whole run.

### Evidence kept in the repository

`evidence --keep [verb...]` copies each named verb's latest current record, or
every current one when none is named, into the repository at
`<record root>/evidence/<record>.txt`, which is `project/evidence/` unless the
profile moves the record with `[record] root`, or under the `evidence_dir` the
profile declares under `[verbs]` (REQ-2956). It asks git whether each kept file
is ignored: an ignored one is named with its rule, left in place, and exits 1,
and where git can't answer it exits 3 (ADR-1550). The file opens with `meow-verbs evidence 1`,
then the verb, the command, the targets, the outcome, the exit status, the tree
id and the time, and holds the whole output; that format is a contract, and the
ledger's own format is private (REQ-2964). A stale record isn't kept. The tree
id leaves the evidence directory out, and `meow-verbs tree <commit>` prints a
commit's tree id the same way (ADR-1530).

### The evidence behind a change's claims

Every record carries the tree id it was collected at, and any change to the
tree makes it stale (REQ-0452, REQ-0454). Where a submodule has uncommitted
changes the tree id is `none`, so a result then is bound to nothing and an
earlier one reads as bound to nothing too, with `evidence` naming the
submodule and exiting 3 (ADR-1560).

`evidence --kept` lists every kept file the work adds against the branch's
base on `trunk` under `[git]`, committed, uncommitted or untracked, each with
its record identifier, verb, outcome, tree id and whether that matches the
tree of `HEAD` less the evidence directory (REQ-0456). The latest file per
verb counts, and an earlier one is listed as `superseded`. It exits 1 where a
counted file failed or differs, else 4 where one was interrupted, else 3
where the listing is empty, the trunk or base is unknown, or a file is bound
to nothing, else 0.

### The ledger as run state

The ledger is run state, kept outside the repository (REQ-3072). Each record
names the repository's identity, the hash of its first commit (REQ-0752). A
missing ledger or an unparseable line reads as absent (REQ-0754).
`meow-verbs state` prints where the ledger is, its record count, the oldest
and newest, and the evidence directory (REQ-0756). Every write takes a lock in
`$XDG_RUNTIME_DIR`, or the user's temporary directory where that is unset, and
a lock older than a minute is replaced (REQ-0758, REQ-2958, REQ-2967).
`MEOWPAW_STATE_DIR` moves the state directory and `MEOWPAW_STATE=off` writes
nothing outside the repository (REQ-2960). The first `run` finding a record
older than 30 days drops those records and their output files, skipping the
prune when the lock is held, and `state --purge` drops all (REQ-2962). Rewrites
go through a temporary file renamed into place, and a reader skips a line cut
short (REQ-2966).

A verb's run is recorded as started, with its process id, start time and host,
and ended in a second line; a start with no end reads as `running` while that
process lives and `interrupted` otherwise, and a verb ended by a signal is
`interrupted` (REQ-2968, REQ-2969). `run` and `evidence` exit 1 where a verb
failed or went stale, else 4 where one was interrupted or is running, else 3
where one was unresolved, else 0. `evidence --all` adds every work tree whose
records name the same repository (REQ-2970).

### The skill

`meow-verbs:verify` carries the obligation to use the program whenever the
model would format, lint, type-check, test or build, in the description form
SPC-1030 states. It runs `status` before the first `run` in a session, so the
commands the profile names are on screen before anything executes, and it
reports each verb with the kind of result the program gave, never rounding an
unresolved verb into a pass. It runs `format` before the other verbs, cites a
result as `evidence` prints it, and calls the work done only when `evidence`
on the verbs the change needs exits 0 or a person accepts what it reported
(REQ-0146, REQ-0148).

### The program

The program is the `verbs` subcommand of the native tool SPC-1080 states,
shipped as a binary inside the unit, so it needs nothing installed on the
machine. The launcher runs the binary for the machine's target, and where
there is none, every verb reports the kind "no interpreter" and nothing reports
passed. The kind keeps the name it had when the program needed an interpreter,
so the fixtures that define it didn't change in the port; it means the program
can't run on this machine.

## Failure paths

| Condition                                     | What happens                                                                     |
| --------------------------------------------- | -------------------------------------------------------------------------------- |
| No profile                                    | Every verb is unresolved, of kind "no profile"; `run` runs nothing and exits 3   |
| The profile doesn't parse                     | Every verb is unresolved, of kind "profile unparseable", with the parser's error |
| A verb's value isn't a string                 | That verb is unresolved, reported as a malformed declaration                     |
| The declared command exits non-zero           | The verb failed: its command, status and whole output, led by its last lines     |
| The declared command isn't found by the shell | The verb failed, with the shell's own message, because the repository named it   |
| No binary for the machine's target            | Every verb is unresolved, of kind "no interpreter"                               |
| `run` with no verb                            | An error naming the five verbs, and nothing runs                                 |
