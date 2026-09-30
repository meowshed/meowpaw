---
id: RES-0301
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0024, RES-0059
---

# The record tells a runner whether a step may start, but not whether it is done or whether a gate was crossed

## Summary

`paw ready` answers whether a step's input is approved, and exits 0 for a
task that is already closed and for a requirement an approved decision already
addresses, so it can bind the start of a run and can't say when the run's step
is done. It exits 1 both for an input that isn't ready and for a record root
that doesn't exist, as SPC-1090 specifies, where it prints that nothing was
checked. The record's
frozen check passes a draft set to `approved`, a withdrawal and an added line
naming an authority, which are the acts the method gives a person, so it can't
tell a run's approval from a person's. An epic's `~` mark counts as finished exactly as `x`
does, and a done task's evidence is text the model writes, so "every task
finished" is met by dropping every task. The tree ids the ledger computes are
tree objects in the repository, and `git diff-tree` between two of them names
each path a call changed, which lets a runner tell which step's files an
iteration touched. Reading the whole record takes 0.23 seconds of wall time,
while the frozen check spent 47 seconds of CPU time on the same record.

This covers what `paw`, the ledger and git 2.55.0 report on this machine, and
what the Claude Code hooks reference says about a hook's environment and how
it denies a call. It doesn't cover a hook firing inside a `claude -p` call,
which nobody observed, or the Edit and Write tools' input as a hook receives
it.

## The question

RES-0024 and RES-0059 concluded that a run completes on evidence at the
current revision and never on a phrase, that the plan's tasks marked with what
closed them are part of that evidence, and that a run stays inside one step
and never crosses an approval gate. They read about loops and ran nothing. A
runner outside the model can hold those rules only through what a program can
read, so the question is what the record and the ledger report that a runner
could read after each iteration: whether the step may start, whether it is
done, whether an approval was written, and which files the iteration changed.

The assumption behind the question is that `paw` already answers these,
because the method gates each step with it. The findings below show it answers
the first and not the other three.

## Method

On 2026-09-29, on this machine, a Mac on arm64 with git 2.55.0 and Claude Code
2.1.280, I ran `paw` from this repository at `main` as #712 left it against a local clone
of the repository in the scratch directory, so no probe touched a work tree
anyone uses:

1. `paw ready implement TSK-3300`, a task already closed, and
   `paw ready design` on the first requirement ADR-2000 addresses.
2. `paw ready bogus TSK-3300`, `paw ready implement` with no identifier, and
   `paw ready implement TSK-3300` after setting the task's `status` to `draft`.
3. `paw ready implement TSK-3300` from an empty directory with no record.
4. `paw check frozen --base HEAD` after each of three edits to the approved
   requirement, restored between them: a line naming an amendment by a
   decision, in the form the frozen check accepts, a `status` changed to
   `withdrawn`, and a plain line of text.
5. `paw check frozen --base HEAD` and `paw status --waiting` on the clean
   clone, each under `/usr/bin/time -p`.
6. In a second local clone, of this record's work tree at #710's merge,
   `ce14ec83`, I committed this record as a draft, set its `status` to
   `approved` without committing, and ran `paw check frozen --base HEAD`
   under `/usr/bin/time -p`. The clone held no other draft at `HEAD`, so this
   record was the one draft to probe.

In a second scratch repository I wrote the working state as a tree twice
through a temporary index, as `ledger::tree_id` does, with an edit to one file
and a new file between them, and ran `git cat-file -t` and
`git diff-tree -r --name-status` on the two ids.

I read the record's program in `crates/meow/src/record.rs` and the ledger's in
`crates/meow/src/verbs/ledger.rs` at `main` as #712 left it, the step files in
`plugins/meow-flow/skills/method/steps/`, the method's skill, SPC-1090's
statement of `ready`, and the Claude Code hooks reference.
I ran no `claude -p` call, so nothing here shows a hook firing in one.

The frozen check's wall time read 6629.50 seconds, which the host sleeping
during the run explains better than the check does, so I report its CPU time
alone.

## Findings

### `paw ready` binds the start of a step and never says the step is done

`paw ready implement TSK-3300` printed `ready; TSK-3300 approved and
complete` and exited 0, though EPC-1900 marks TSK-3300 done. `paw ready design`
on the first requirement ADR-2000 addresses exited 0 the same way. The
program checks that each input is approved and, for `cover` and `implement`,
that the task's epic is approved, its dependencies are done and its `## Cover`
section is filled; for `epic` that every requirement the decision addresses is
stated by a specification; for `document` and `verify` that every task of the
epic is done; and for `review` that the epic's `checked-at` is set
(`record.rs`, `fn ready`). It reads no output of the step it gates.

### `paw ready` exits 1 for a missing record as for an input that isn't ready

A draft input printed `not ready`, then `TSK-3300, a task, is draft and not
approved`, and exited 1. An unknown step and a missing identifier each exited
with status 2. From a directory with no record, the program printed `the
record's root ... doesn't exist; nothing was checked` and exited 1.
SPC-1090 specifies that exit for a missing root, "as `check` does", and
reserves exit 3 for a machine the unit carries no binary for. The method's
skill reports exit 3 as a record not checked and exit 1 as what is missing, so
it reads a missing root as a missing input. A program reading the exit status
alone reads a missing record as an input that isn't ready.

### The frozen check passes the two forms a person uses to change an approved record

After a line naming an amendment by a decision was appended to an approved
requirement, `paw check frozen --base HEAD` printed `frozen: 0 findings` and
exited 0. After its `status` was set to `withdrawn` it printed the same. After
a plain line was appended it printed `approved at HEAD, and changed since
without a line naming its authority` and exited 1. The program skips a record
whose status is now `withdrawn` or `superseded`, skips one gaining a line that
matches its authority pattern, and allows an approved epic to change while its
`checked-at` is empty, and an approved task or defect to change outside its
frozen part (`record.rs`, the frozen comparison). Each exemption is a decision
the method gives a person, so a run that wrote one passes the check.

After a draft committed at `HEAD` had its `status` set to `approved`, the same
command printed `frozen: 0 findings` and exited 0, in 41.75 seconds of wall
time and 32.51 seconds of CPU time. The comparison reads only the records whose
status was `approved` at the base revision, so a draft that becomes approved
is outside what it reads. An approval, the act a run must not perform, passes
the frozen check as the two exemptions do.

### An epic's dropped mark counts as finished

`marks` reads each task line of an epic with its mark, and `finished` returns
true for `x`, done, and for `~`, dropped (`record.rs`, `fn marks` and
`fn finished`). `task_finished`, which `paw ready` uses for dependencies, reads
through the same function. A test that every task of an epic is finished
therefore holds when every task is dropped.

### A done task's evidence is the task's own text, bound to no tree

The record's rule `done-has-evidence` reports an epic that marks a task done
while the task's `## Evidence` section holds nothing past "Not yet."
(`record.rs`). It reads that the section holds text, and not what the text
cites. TSK-3300's Evidence cited a kept run file (Corrected by ADR-2300,
which removed kept files and with them this path), a run
kept in the cover commit, before the implementation existed, so the citation
shows the check failing before the work and not passing after it.
I read TSK-3300 alone, so this shows the rule accepts such a citation, and not
how often closed tasks make one.

### The ledger's tree ids name the paths an iteration changed

The two tree ids read `251ea31d` and `9cdaa92d`; `git cat-file -t` printed
`tree` for the second, and `git diff-tree -r --name-status` between them
printed `A project/requirements/REQ-2.md` and `M src/x` and exited 0.
`ledger::tree_id` writes the tree the same way, through `git add --all` and
`git write-tree` on a copy of the index, leaving the evidence directory out
(`ledger.rs`, `fn tree_id`). A runner that already takes the tree id before
and after a call can therefore list the paths the call changed without
another pass over the work tree.

### The ledger is a file any process that can write the state directory can append to

`ledger::record` appends one JSON line holding the verb, the command, the
outcome, `tree_before` and `tree` to a file under the state directory, outside
the work tree, with no signature (`ledger.rs`, `fn record`). A pass recorded
there says a process wrote that line, and not that the runner saw the command
pass.

### The step files name where each step's artifact lands

Each file in `plugins/meow-flow/skills/method/steps/` opens by naming the
step's input and where its artifact lands: research in `research/`,
requirements in `requirements/`, design in `adrs/`, spec in `specs/`, epic in
`epics/` and `tasks/`, verify in the epic, all under the record root; cover in
the check files and the kept failing run; implement in the changed files, the
kept runs and the task; document in each user-facing page it changed; and
review writes nothing into the repository. `paw` names each kind's gate:
research, requirements, design for a decision, epic for an epic or a task,
and triage for a defect (`record.rs`, `fn gate_of`).

### Reading the record is fast, and the frozen check is not

`paw status --waiting`, which reads every record file to list the drafts, took
0.23 seconds of wall time on the clone's 2146 files. `paw check frozen --base
HEAD` on the same clean clone spent 17.66 seconds of user and 29.84 seconds of
system CPU time, in one timed run on a host that slept during it. Reading
`record.rs`, the check reads each record's text at the base revision through
git, which I take to be where the time goes; I didn't measure where it goes.

### A hook inherits Claude Code's environment and denies a call by its output

The hooks reference says a hook command inherits the parent environment from
Claude Code, apart from the `OTEL_*` exporter variables and whatever
`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` strips, and that a `PreToolUse` hook
denies a call by printing `permissionDecision: "deny"` or by exiting 2. It says
hooks fire in `-p` mode. It doesn't document the `tool_input` fields of Edit
and Write. The tools as this session's schema presents them on 2.1.280 take
`file_path`, `old_string`, `new_string` and `replace_all` for Edit, and
`file_path` and `content` for Write.

## Conclusions

1. A runner can refuse a step whose input isn't approved by applying the test
   `paw ready` applies, but it needs a separate test of whether the step's
   work is done, because `paw ready` passes before and after the work alike.
2. A program reading `paw ready`'s exit status alone can't tell a missing
   record from an input that isn't ready, because both exit 1; only the
   printed line tells them apart.
3. A run can't use the frozen check to find an approval it wrote, because the
   check passes a draft set to `approved`, a withdrawal and a line naming an
   authority, which are exactly the changes a run must not make on its own.
4. A test of whether an epic's tasks are done has to read the `x` mark and not
   the `~` mark, or dropping the work satisfies it.
5. The evidence that a run's work holds at the current tree has to come from
   checks run at that tree, because a task's Evidence section is text the
   model writes, and `done-has-evidence` accepts a citation of a run kept
   before the implementation existed, as TSK-3300's shows.
6. A runner has to run the checks itself to trust a pass, because a line in
   the ledger doesn't show the runner saw the command pass.
7. A runner can compare the record after each call with the record as it read
   it at the start at little cost, and can list the changed paths from two
   tree ids it already takes. The reading costs 0.23 seconds, measured through
   `paw status --waiting`, which reads the same files. Matched against where
   the step files say each step's artifact lands, the listed paths tell the
   runner whether a call stayed inside its step, as RES-0059 requires.
8. The case against running the checks after every call is their cost. The
   frozen check alone spent 47 seconds of CPU on this record in its one timed
   run, so running it after each of 20 calls, for example, would spend about 16
   minutes of CPU on a check the in-memory comparison replaces. The verbs cost
   whatever the repository's commands cost, which this research didn't
   measure. I infer, without having built or measured one, that a comparison
   against the copy held at start could replace the frozen check after each
   call for about the 0.23 seconds the read takes. The two differ in their
   baseline. The comparison would catch what the frozen check passes: a
   draft set to `approved`, a withdrawal, a line naming an authority, and a
   record deleted since the start. The frozen check catches what the
   comparison would not: a change to an approved record made before the run
   started, since the base revision, which the copy already holds. A runner
   can run the verbs only after a call that changed the tree. Only the verbs,
   run at the tree that stands, are needed at the step's end.
9. The strongest case against that leading option, comparing the record in
   memory and listing paths from tree ids, is that a comparison only sees
   change and can't tell a permitted change from a forbidden one. The
   requirements, design, spec and epic steps write into the record by
   design, and the implement and verify steps change approved epics in
   defined places, so a runner needs a separate statement, per step and per
   kind, of which changes are allowed. That statement duplicates what the
   frozen comparison and the step files already say, and it can drift from
   them when the record's rules change. The option is only as strong as that
   second statement, which this research didn't write.
10. A hook that denies a write only inside a run can read a variable the runner
    sets in each call's environment, as far as the documentation says. Before
    anything relies on it, somebody has to observe a `PreToolUse` hook seeing
    a variable set in a `claude -p` call's environment.

## Sources

- `crates/meow/src/record.rs` at `main` as #712 left it, read 2026-09-29 - `fn ready`, the
  frozen comparison, `fn marks`, `fn finished`, `fn task_finished`, the rule
  `done-has-evidence` and `fn gate_of`.
- `crates/meow/src/verbs/ledger.rs` at `main` as #712 left it, read 2026-09-29 - `fn tree_id`
  and `fn record`.
- The step files at `main` as #712 left it, read 2026-09-29 -
  `plugins/meow-flow/skills/method/steps/*.md`, where each step's artifact
  lands.
- TSK-3300 at `main` as #712 left it, read 2026-09-29 - a closed task citing evidence kept
  at an earlier tree.
- EPC-1900 at `main` as #712 left it, read 2026-09-29 - the epic marking TSK-3300 done.
- ADR-2000 at `main` as #712 left it, read 2026-09-29 - the first requirement it
  addresses, probed with `paw ready design`.
- `plugins/meow-flow/skills/method/SKILL.md` at `main` as #712 left it, read 2026-09-29 -
  how the method's skill reads `paw ready`'s exit 1 and exit 3.
- SPC-1090 at `main` as #712 left it, read 2026-09-29 - `ready`'s exit statuses, in The
  gate and Failure paths.
- `paw` at `main` as #712 left it and git 2.55.0, read 2026-09-29 - the exit statuses,
  messages, timings and tree ids above, from `paw ready`, `paw check frozen`
  and `paw status --waiting`.
- [Hooks reference](https://code.claude.com/docs/en/hooks), read 2026-09-29 -
  a hook's inherited environment, the `PreToolUse` deny forms, and hooks in
  `-p` mode.
- The Edit and Write tool schemas, read 2026-09-29 - the input fields each tool
  takes, as Claude Code 2.1.280 presents them to a session.
