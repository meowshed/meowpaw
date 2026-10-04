---
id: ADR-1590
artifact: adr
status: done
revised: 2026-09-27
addresses: [REQ-2480, REQ-2486, REQ-2487, REQ-2508, REQ-2510]
postpones: [REQ-2488]
supersedes: []
---

# 1590. A go-task pack reads a Taskfile without writing to it, and binds a verb only to a task that can run unattended

## Decision

A new pack, `meow-gotask`, ships a program with `status`, `bind` and `check`
and a skill that tells the model to use them. It does for Task what ADR-1580's
`meow-mise` does for mise, and keeps every rule SPC-1140 states: a static
detection first, a listing reported as resolved, each task's origin and
replacement, the blocks that stop binding, exact names, `--force` and exit
status 3 for every state that would otherwise read as "no tasks".

What differs is where each fact comes from, because Task's listing carries
less than mise's and writes where mise's doesn't (RES-0127):

- Detection reads the eight Taskfile names RES-0123 lists at the repository's
  root, and starts no Task where none exists.
- The listing runs `task --list-all --json` with `TASK_TEMP_DIR` set to a
  directory the program creates outside the repository and removes after, so
  listing writes nothing into the repository and makes no later run skip a
  task that never ran.
- Everything the listing leaves out is read from the file its
  `location.taskfile` names, found under the task's name with each include
  namespace stripped in turn. From that definition come the blocks: `internal`,
  `prompt` as asking for a person, `requires` as needing variables (REQ-2508),
  and `ignore_error` on the task or any of its commands as ignoring errors
  (REQ-2480). A task that ignores errors also says that a verb bound to it
  can't report the failure it ignores. Task has no other setting that hides a
  failure: `silent` hides the echoed command, which RES-0123's schema shows.
- A task whose `if` or `platforms` is set is blocked as running only under a
  condition, because RES-0127 saw both exit 0 without running, even under
  `--force`, so a verb bound to one could pass having run nothing.
- Those blocks follow a task's `deps` and each `task:` its `cmds` call, to any
  depth, and a block found that way names the task it came from, as in
  `ignores errors, through lint`. A dependency is looked up in the listing,
  under the calling task's namespace first and then as written, because only
  Task resolves include namespaces and templated include paths, and the
  listing names each task's file. A task that depends on one ignoring its
  errors passes on that failure too, so it is blocked the same way.
- A task with `status`, or with `sources` under a `method` other than `none`,
  can skip as up to date, and `status` names what decides it: its `status`
  commands, or the checksum or timestamp of its sources, by the task's
  `method`, the Taskfile's, or checksum where neither sets one.
- A task the Taskfile declares `internal`, which the listing leaves out, is
  reported by `bind` and `check` as internal, never as missing.

Before anything is listed, `status` reads each committed Taskfile and the
local Taskfiles it includes for a remote include, a `taskfile` naming a URL or
a `git::` source, and reports each one with its namespace and source
(REQ-2486). Where one exists it runs no listing and reports `unresolved:
remote include`, exit status 3, because a listing fails with 104 or 106 unless
something trusts a host, and RES-0127 found that the temporary directory hides
even the trust a person gave. A 104 or 106 that an include the static read
misses still causes is reported as a remote Taskfile the listing can't see,
never as untrusted, since the person may have trusted it. The program never passes `--yes`, `--trusted-hosts`, `--download` or
`--insecure`, because each either answers a prompt the author meant for a
person or lets a third party's code into the person's environment.

`check` reports a remote include in a committed Taskfile as a finding, and the
skill forbids writing one (REQ-2487). A harness that authored one couldn't
pass a gate that runs `check`, and a person who added one sees it named.

`status` names each variable a committed Taskfile marks `secret: true`, as
`masked in Task's output, not protected`, and never prints its value
(REQ-2510). The skill says a masked value is still in the process's
environment and output a program captures before masking.

`bind` binds a verb as `task --force <name>`, so a task Task would skip runs,
and `check` finds a bound task that can skip run without `--force` or `-f`.
RES-0127 observed `--force` running a task's `deps` too, so a dependency that
can skip runs as well.

The pack reads `requires` before anything runs, and a task needing a variable
is never bound (REQ-2508). A verb that runs one anyway, written by hand, meets
Task's own exit 206 naming the missing variable, and `check` reports that
binding as needing variables before it runs. The same holds for a prompt's 201
and an internal task's 202.

REQ-2488 is postponed. It asks the harness to surface a changed remote
checksum as a supply-chain event, and RES-0127 found that without a terminal
Task fails a changed remote Taskfile exactly as one nobody trusted, with 104
and the same line. The pack never fetches a remote Taskfile, so it never
causes the check either. It comes when the harness runs Task where a person
answers, or when Task tells a program that the checksum changed.

After this decision a repository using Task gets its verbs bound to its own
tasks, with a task that ignores errors, needs a variable, asks for a person or
comes from a remote include reported instead of bound, and listing it no
longer poisons its freshness. What still doesn't work:

- A repository with a remote include gets no listing at all, only the
  include named.
- A task that ignores errors through a shell construct, such as `|| true`,
  isn't found, because the pack never reads a task's commands (REQ-2492).
- A verb written by hand to run a task that needs a variable meets Task's
  exit 206, and `meow-verbs` reports it as a failed verb whose last lines
  name the missing variable; it reads as a missing input only where `check`
  ran first, as a repository's gate can make it.
- just and make have no pack.

## Why

RES-0123 found that Task's listing is machine-readable and namespaced, that a
remote include needs trust Task stores as a checksum, that `status` and
`sources` skip a task and exit 0, and that `requires`, `ignore_error` and
`secret` each change what a result shows. RES-0127 observed that the listing
carries none of those fields, that listing writes a checksum which makes the
next run skip, that `TASK_TEMP_DIR` prevents it, and that without a terminal a
changed remote checksum can't be told from an untrusted file.

## Alternatives

| Option                                                           | Better at                                    | Why it lost                                                                                             |
| ---------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| List without moving `TASK_TEMP_DIR`                              | No temporary directory                       | Writes into the repository and makes the next run skip a task that never ran                            |
| Parse the Taskfile alone, never list                             | Starts no Task at all                        | Task resolves templated include paths, OS variants and flattened includes, and a parse would guess them |
| List with `--offline` where a remote include is                  | A listing even with a remote include         | With the temporary directory nothing is cached, so it always fails with 106, and says nothing more      |
| Fold go-task into `meow-mise`                                    | One unit                                     | Each runner's trust, freshness and listing differ, and a repository pays for a runner it lacks          |
| Bind a skipping task without `--force`, reported as able to skip | No repeated side effect of a guarded command | A skip exits 0, and `silent: true` hides its line, so a verb could pass on a run that never happened    |
| Do nothing                                                       | No new unit                                  | Five requirements stay unmet, and a Task repository writes each verb by hand                            |

## What it costs

Every repository that installs the pack keeps its skill description in context
on every turn. The person running any of the three commands runs Task twice,
for the version and the listing, and the program parses every committed
Taskfile. RES-0127 saw the listing run neither a `status` command nor an `sh:`
variable, so on 3.53.1 listing ran none of the repository's commands.

Whoever waits on a gate pays for a task and its `deps` run again under
`--force`. A repository whose `status` guards a command that isn't idempotent,
such as one that creates something if it's absent, pays more: forcing it
repeats the side effect or fails. A repository with a remote include gets
nothing listed until it drops the include or a later decision fetches.

A repository whose `test` task declares `requires` gets no binding for it,
even where CI always supplies the variable; it writes that verb by hand, and
`check` then reports the binding until the requirement is dropped.

Whoever maintains `crates/meow` takes on a YAML parser, a new dependency behind
the `gotask` feature alone. Moving the code the two packs share changes
`meow-mise`, which has shipped; its 38 fixtures run unchanged against the
moved code, and the change is reverted if one fails.

## What would reverse it

I would drop `TASK_TEMP_DIR` if Task stopped writing checksums when it lists,
and revisit listing at all if a later Task ran `sh:` variables while listing,
since the listing would then run the repository's code.
I would drop the Taskfile parse and its YAML parser if the listing carried
`requires`, `ignore_error`, `prompt`, `internal`, `status`, `sources` and
`method`. I would drop `--force` if Task told a skip from a pass by its exit
status or in its JSON.
I would list a repository with a remote include if the harness gained a way to
read Task's cache without writing it. I would take up REQ-2488 if Task started
reporting a changed checksum to a program without a terminal.

## Consequences

- A unit `meow-gotask` with a program, a skill, a README, a budget and a
  marketplace entry.
- A native feature `gotask` in `crates/meow`, built by `build-units`, and a
  YAML parser in the crate behind that feature alone.
- The code both runner packs share moves into one module the two features
  compile.
- A specification of the pack, SPC-1150.

## How I will know it was realised

1. Fixtures with real Task show `status` reporting a committed task with no
   block, and an internal, a prompting, a variable-requiring and an
   error-ignoring task each with its block, and a task depending on the
   error-ignoring one blocked through it. They also show a task from an
   include with its namespace, and a task that can skip with what decides it.
2. A fixture lists a Taskfile whose task declares `sources`, then runs that
   task with Task, and the task runs; `git status --porcelain --ignored`
   reads as before after all three commands.
3. A fixture with a remote include shows the include named, the report
   unresolved for it with exit status 3, and no listing run; `check` reports
   the include as a finding. A stand-in Task exiting 104 or 106 is reported as
   untrusted or not cached.
4. A fixture shows a `secret: true` variable named as masked and not
   protected, with its value absent from the output.
5. Fixtures show `bind` binding `test` as `task --force test` and leaving a
   blocked task unbound with its reason, and `check` exiting 1 on a skippable
   task run without `--force`.
6. Fixtures show `check` reporting a hand-written binding to an internal, a
   prompting and a variable-requiring task, each with its block and none as
   missing, and `status` blocking an `if` and a `platforms` task.
7. Every requirement ADR-1590 addresses lands in exactly one closed task, and
   REQ-2488 reads as postponed.

## What this does not settle

- REQ-2488, until a program running Task can see a changed checksum.
- Listing a repository with a remote include.
- Packs for just and make.
