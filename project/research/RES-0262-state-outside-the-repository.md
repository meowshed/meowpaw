---
id: RES-0262
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0031, RES-0261
---

# State outside the repository

## Summary

The synthesis concluded that run state lives outside the repository keyed by
git root, and no document says what is in it, where it goes, or who removes it.
The desktop specification already draws the line the harness needs: state is
what persists between restarts and is not important or portable enough to be
data. The platform demonstrates the whole pattern, hazards included. A
per-project directory derived from the working directory's path, a retention
sweep with a configurable period, and an explicit warning that the file format
is internal and changes between releases. This project ignored that warning
earlier today, which we record here.

Research for the files the harness keeps per machine. It does not cover the
repository's own declaration, which is
[RES-0261-the-profile.md](RES-0261-the-profile.md), nor the evidence the record
carries, which is [RES-0031-routing.md](RES-0031-routing.md).

## The question

Two things pull in opposite directions. Everything that is evidence belongs in
the repository, because the record has to be readable without the harness and
has to outlive it. And a pending gate, a run's position and a cache of computed
answers are not evidence, are per machine, and would be noise in a diff.

So: what is outside, where exactly, and what happens to it.

## Method

We fetched and read the desktop base-directory specification on 2026-09-20 for
the four user directories and the runtime directory. We quote its definitions
in full, because the distinction between state, data and cache is the finding.

The platform's session documentation was fetched and read for a working
implementation of the same pattern: where transcripts go, how the per-project
directory name is derived, what retention applies, and what is restored on
resume.

The surveyed harness that keys its state by git root was read from its
repository, through the survey document already in this corpus.

Nothing was built. No state file was designed or written, and no crash was
induced to observe recovery.

## Findings

### The specification already names the category, and it is not data

The four user directories and their defaults: configuration under
`$HOME/.config`, data under `$HOME/.local/share`, state under
`$HOME/.local/state`, and cache under `$HOME/.cache`.

State is defined precisely, and the definition fits the harness's needs exactly:

> state data that should persist between (application) restarts, but that is
> not important or portable enough to the user that it should be stored in
> `$XDG_DATA_HOME`

with examples that read like a list of what a harness keeps: actions history - logs, history,
recently used files - and the current state of the application that can be
reused on a restart, such as the layout, the open files and the undo history.

So the harness's run state is state, and neither data nor cache. The
distinction has consequences. A user backing up their home directory includes
data and may exclude state and cache, which is the correct outcome: losing the
harness's run position costs a resumption, and losing the record would cost the
project.

A fifth directory holds runtime objects under hard requirements: owned by the
user, mode 0700, _"The lifetime of the directory MUST be bound to the user
being logged in"_, and files in it _"MUST not survive reboot or a full
logout/login cycle."_ A lock or a socket belongs there, and nothing the harness
needs to survive a reboot may live in it.

### The platform demonstrates the pattern, including the part that bites

Transcripts are stored at a path built from the configuration directory, a
project directory and a session identifier, where the project directory is
_"your working directory path with non-alphanumeric characters replaced by
`-`"_. Over two hundred characters, the name is truncated and a hash of the
full path appended so it stays within filesystem limits.

Three mechanisms come with it and each answers a question this research has to:

Relocation. One environment variable moves the whole directory, and a
second names the project directory explicitly - with the stated rule that the
second without the first merges every project into one directory.

Retention. A sweep with a default period of thirty days, configurable, plus
a command that purges a project's data sooner.

Suppression. An environment variable that stops transcript writes
entirely, and a flag that suppresses them for one non-interactive run.

The last one matters more than it looks. A harness that cannot be told to write
nothing outside the repository is a harness that cannot be used where that is
the rule.

### The format warning, and this project ignoring it

The platform states the hazard plainly:

> The entry format is internal to Claude Code and changes between versions, so
> scripts that parse these files directly can break on any release.

Earlier in this project's own work, the transcript was parsed directly to
recover what had been done. It worked, and the warning stands: that code is
correct today and has no guarantee tomorrow.

The lesson for the harness's own state is the inverse obligation. Where the
harness writes state that anything else may read, its own later versions
included, one of two things has to be true. Either the format is a stated
contract with a version, or it is internal and nothing parses it. The failure
is a format that is neither: not promised and read anyway.

### Keying by git root is right and is not sufficient

The surveyed harness keys its state by git root, which is the obvious choice:
it is stable across sessions, identical for everyone in the repository, and
survives the working directory moving within the tree.

Two cases break it, and both are ordinary here.

Worktrees. Several worktrees of one repository share a git root in the
sense that matters to git and are different working trees with different
checked-out branches. State keyed on the root alone would have parallel runs
overwriting each other's position - which is precisely the arrangement the
delegation research recommends. The platform's own answer is to key per
directory and then offer to widen the view across worktrees, which is the
better default: separate by directory, aggregate on request.

Two clones of the same repository. Same remote, different paths, different
branches, possibly different states of work. Keyed by remote they collide;
keyed by path they do not.

So: keyed by working tree path, with the repository identity recorded inside
the state, and encoded nowhere in its location.

### What goes outside, and what must not

Outside, because it is per machine and is not evidence:

- The run's position: which step, which unit of work, what it is waiting on. -
  The pending gate: the fact that one is pending, where the approval itself
  lives in the record. - Caches of computed answers: resolved verbs, detected
  packs, parsed profiles. - Logs of what the harness did, as distinct from what
  it found.

Inside, because it is evidence or is the record:

- Every artifact.
- Every gate record: what was approved, by whom, when, at which revision.
- Every piece of evidence a verb produced.

The line is whether a second person on another machine needs it to trust the
work. An approval does; the knowledge that the harness is currently waiting for
one does not.

The tempting middle case is evidence itself - a captured test output is large,
uninteresting in a diff, and would be convenient to keep outside. It cannot be:
evidence that lives on one machine is evidence nobody else can check, which
makes it an assertion.

### Crash and resume have a documented behaviour this harness copies

The platform states what a resumed session restores and what it does not. One
line is the model for the harness's own recovery: a tool that was still running
when the previous process ended _"doesn't finish or run again when you
resume"_.

That is the honest behaviour. The alternative - re-running whatever was in
flight - repeats side effects that may have already happened.

So the harness's state records what it _started_ as well as what it finished,
and on resume it reports the interrupted step and retries nothing. An
interrupted gate is reported as interrupted, which is a fourth outcome beside
pass, fail and unresolved, and it is the honest report, where a silent re-run
hides what happened.

### Concurrency is real here and is usually forgotten

Two sessions in two worktrees of one repository are the intended arrangement.
Two sessions in the _same_ directory are not intended and happen anyway - the
platform notes that resuming one session in two terminals interleaves both
into one transcript.

A state file written by two processes without care is corrupted, which is worse
than wrong. The remedies are old and cheap. Write to a temporary file and
rename it into place, so a reader sees either the old state or the new one and
never half of either. And take a lock for the read-modify-write case, in the
runtime directory and never beside the state.

## Conclusions

1. Run state is state, and neither data nor cache, and lives under the
   platform's state directory, because it persists between restarts and losing
   it costs a resumption and never the project. 2. The record stays in the
   repository. Every artifact, every gate record and every piece of evidence,
   because a second person on another machine needs them to trust the work. 3.
   Evidence is never kept outside, however large, since evidence that lives on
   one machine is an assertion. 4. State is keyed by working tree path, and
   never by git root or remote, because worktrees and second clones both
   collide otherwise. 5. The repository's identity is recorded inside the
   state, and encoded nowhere in its location, so state can be found by either. 6. Aggregation across worktrees is offered, and assumed never, following the
   platform's separate-by-default and widen-on-request behaviour. 7. A lock or
   socket goes in the runtime directory, which is user-owned, mode 0700, and
   whose contents must not survive a reboot. 8. The state directory is
   relocatable and writing it is suppressible, because a harness that cannot be
   told to write nothing outside the repository cannot be used where that is
   the rule. 9. Retention is bounded and purging is possible, so nothing
   accumulates indefinitely. 10. The state format is either a versioned
   contract or internal and unread by anything else. A format that is neither
   promised nor private is the failure, which this project demonstrated by
   parsing the platform's own transcripts against its stated warning. 11. State
   is written atomically, through a temporary file renamed into place, so a
   concurrent reader sees one version or the other. 12. A read-modify-write
   takes a lock, because two sessions in one directory happen whether or not
   they are intended. 13. An interrupted step is recorded as started and is
   reported as interrupted on resume, never silently retried, because retrying
   repeats side effects that may already have happened. 14. Interrupted is a
   fourth gate outcome beside pass, fail and unresolved.

## Sources

All read 2026-09-20.

- [XDG Base Directory Specification](http://specifications.freedesktop.org/basedir/latest/)
  - the four user directories and their defaults; the definition of state as
    data that persists between restarts but is not important or portable enough
    to be data, with its examples; the distinction from cache as non-essential;
    and the runtime directory's requirements of user ownership, mode 0700,
    lifetime bound to the login session, and contents not surviving a reboot.
- [Manage sessions](https://code.claude.com/docs/en/sessions) - transcripts
  stored per project directory under the configuration directory, with the
  project name derived from the working directory path and truncated with a
  hash beyond two hundred characters; relocation through the configuration
  directory variable and the project-name variable, with the stated rule that
  the second without the first merges projects; the thirty-day retention
  default, its setting, and the purge command; the suppression variable and the
  per-run flag; the statement that the entry format is internal and changes
  between versions so scripts parsing it can break on any release; that a
  resumed session does not finish or re-run a tool that was in flight; the
  per-directory storage with widening across worktrees on request; and that
  resuming one session in two terminals interleaves both into one transcript.
- [RES-0003-external-harnesses.md](RES-0003-external-harnesses.md) - the
  surveyed harness that keeps state outside the repository keyed by git root.
- [RES-0016-delegation.md](RES-0016-delegation.md) and
  [RES-0143-worktrunk.md](RES-0143-worktrunk.md) - parallel work in several
  worktrees as the intended arrangement, which is what makes the keying
  question live.
