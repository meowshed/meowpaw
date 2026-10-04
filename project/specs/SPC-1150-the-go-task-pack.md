---
id: SPC-1150
artifact: spec
status: live
revised: 2026-09-27
states: [REQ-2480, REQ-2486, REQ-2487, REQ-2508, REQ-2510]
---

# The go-task pack

## Scope

This covers `meow-gotask`, the pack that reads what Task resolves in a work
tree and binds the five verbs to the tasks a repository declares. It states
what `status` reports, what `bind` prints, what `check` finds, and how each
unresolved state reads.

Every rule SPC-1140 states for `meow-mise` holds here with Task in mise's
place, and this document states only where the two differ: detection, the
listing, where each block comes from, remote includes and secret variables.
Running a verb is SPC-1040's.

ADR-1590 decides this part, EPC-1560 realises it, and `meow-gotask` implements
it, checked at #587.

## Boundary

| Surface                                      | What it is                                                     |
| -------------------------------------------- | -------------------------------------------------------------- |
| `plugins/meow-gotask/bin/meow-gotask`        | The program: `status`, `bind` and `check`                      |
| `plugins/meow-gotask/skills/gotask/SKILL.md` | The skill that tells the model to use the program, never guess |
| `plugins/meow-gotask/README.md`              | The unit's page                                                |
| `.meowpaw/profile.toml`, `[verbs]`           | What `check` reads; the pack never writes it                   |

The program writes nothing into the repository. It runs `task --version` and
`task --list-all --json`, the second with `TASK_TEMP_DIR` set to a directory it
creates in the system's temporary directory and removes before it exits. It
never runs a task and never passes `--yes`, `--trusted-hosts`, `--download`,
`--insecure` or `--force` to a listing.

The pack was tested on Task 3.53.1, and that version is the line between an
environment failure and a defect in the pack. Exit status is as SPC-1140
states: 0, 1 for a `check` finding, 3 for an unresolved state and 2 for a
usage error.

## Behaviour

### Detection

A work tree is a Task repository when its root holds `Taskfile.yml`,
`taskfile.yml`, `Taskfile.yaml`, `taskfile.yaml` or the `.dist` form of any of
the four, and the program runs no `task` command otherwise.

### Remote includes

Before it lists anything, `status` reads each committed Taskfile at the root
and each local Taskfile it includes, following local includes to any depth. An
include whose `taskfile` names a URL, `http://` or `https://`, or a `git::`
source is remote, and each is reported as `remote include <namespace>:
<source> (<file>)` (REQ-2486). Where there is one, the program lists nothing
and reports `unresolved: remote include`, exit status 3.

### What `status` reports

In this order: Task's version, each remote include, the tasks under `tasks
resolved in this work tree, which may differ from what the repository
declares:`, and the secret variables.

Each task carries its origin and source as SPC-1140 states, from the listing's
`location.taskfile`. Its other facts come from its definition in that file,
found under the listed name, and then with each leading `<namespace>:` removed
in turn until a task of that name is found. A task whose definition can't be
found or parsed carries `unknown definition` as a block.

| Block                    | When the definition                                                         |
| ------------------------ | --------------------------------------------------------------------------- |
| `asks for a person`      | sets `prompt`                                                               |
| `needs variables <vars>` | sets `requires.vars`, each named (REQ-2508)                                 |
| `ignores errors`         | sets `ignore_error: true`, on the task or on any entry of `cmds` (REQ-2480) |
| `runs only if <cond>`    | sets `if`, which exits 0 without running even under `--force`               |
| `runs only on <list>`    | sets `platforms`, which does the same on another platform                   |
| `not committed`          | comes from a file git doesn't track, or from outside the work tree          |

Each block also follows the task's `deps` and each `task:` entry of its
`cmds`, to any depth, and a block found that way names its task, as in
`ignores errors, through lint`. A dependency is looked up in the listing under
the calling task's namespace first, then as written.

A task that ignores errors also carries `a verb bound to it can't report the
failure it ignores` (REQ-2480). A task with `status`, or with `sources` under a
`method` other than `none`, carries `can skip as up to date`, with what decides it: `decided by its status commands`
where it sets `status`, and otherwise `decided by the <method> of its
sources`, where `<method>` is the task's `method`, the Taskfile's, or
`checksum`.

Under `secret variables:` it names each variable a committed Taskfile marks
`secret: true`, globally or in a task, as `<name> (<file>): masked in Task's
output, not protected`, and never prints a value (REQ-2510).

### What `bind` prints

As SPC-1140 states, with each binding as `<verb> = "task --force <name>"`. A
verb whose task a committed Taskfile declares `internal: true`, which the
listing leaves out, is printed as `# <verb>: task <name> is internal`.

### What `check` finds

As SPC-1140 states, where a part of a verb's command that starts `task` names
the first word after its flags as the task, and `--force` or `-f` among those
flags forces it. Each remote include in a committed Taskfile is a finding,
`remote include <namespace>: <source>`, whether or not a verb runs a task from
it (REQ-2487). A task a committed Taskfile declares `internal` is the finding
`task <name> is internal`.

## Failure paths

Each is reported as unresolved, with exit status 3, by all three commands:

| State                              | Reported as                                                                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| No Taskfile at the root            | `unresolved: not a Task repository`                                                                                       |
| `task` isn't on `PATH`             | `unresolved: task not found`                                                                                              |
| A committed Taskfile doesn't parse | `unresolved: <file> doesn't parse: <message>`                                                                             |
| A remote include                   | `unresolved: remote include`, after each is named                                                                         |
| The listing exits 104 or 106       | `unresolved: a remote Taskfile this listing can't see, since it reads no trust or cache`                                  |
| Task rejects a flag                | `unresolved: environment: task <version> predates <flag>`, or `unresolved: meow-gotask defect: <flag>` at or above 3.53.1 |
| Another listing shape              | `unresolved: unrecognised shape: <first 200 characters>`                                                                  |
| Any other failure                  | `unresolved: task failed with exit status <n>: <last lines>`                                                              |

A listing is recognised as an object whose `tasks` is an array of objects each
holding a string `name` and a `location` object holding a string `taskfile`.
