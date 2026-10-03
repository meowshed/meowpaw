---
reader: someone choosing or running meow-gotask
answers: what meow-gotask does, what it adds to a session and how to run it
kind: reference
describes: [meow-gotask@0.2.0]
---

# meow-gotask

`meow-gotask` reports the tasks Task (go-task) resolves in your repository,
where each came from and what would stop a check running it unattended. It
never trusts a remote Taskfile, answers a prompt, runs a task or writes into
your repository. It installs on its own, with no other part of the `meowpaw`
harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-gotask@meowpaw
```

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-gotask status
```

From your own shell, run the same launcher by its path in the installed unit.

It prints Task's version, then every task Task resolves in this work tree,
each with its origin: `repository` for a file git tracks, `work tree only` for
a file git doesn't track, such as a local `Taskfile.yml` beside a committed
`Taskfile.dist.yml`, and `outside` for a file beyond the work tree.

Task writes a checksum into `.task/` whenever it lists tasks, and the next run
of such a task then skips it, although it never ran. The program lists with
`TASK_TEMP_DIR` pointing at a directory of its own outside your repository,
and removes it after, so listing changes nothing.

Task's listing names each task and its file and nothing else, so the program
reads each task's definition from the Taskfile. Under a task, `blocked:` names
what stops a check running it unattended, and a block a task takes on from a
dependency or a task it calls names that task, as in `ignores errors, through
lint`:

| Block                    | Means                                                        |
| ------------------------ | ------------------------------------------------------------ |
| `asks for a person`      | It sets `prompt`                                             |
| `needs variables <vars>` | It sets `requires`, so it fails for a missing input          |
| `ignores errors`         | It sets `ignore_error`, so it exits 0 on a failure           |
| `runs only if <cond>`    | It sets `if`, and exits 0 without running when that is false |
| `runs only on <list>`    | It sets `platforms`, and exits 0 without running elsewhere   |
| `not committed`          | It comes from a file git doesn't track, or from outside      |
| `unknown definition`     | The program couldn't find or read its definition             |

A task with `status`, or with `sources` under a `method` other than `none`,
carries `can skip as up to date` and what decides it.

Under `secret variables:` it names each variable marked `secret: true`, never
its value. Task masks such a value only in the command it echoes, and the
command's own output still prints it.

## Remote includes

Before it lists anything, the program reads your Taskfile and every local
Taskfile it includes for an include naming a URL or a `git::` source, and
names each one. Where there is one, it lists nothing and reports `unresolved:
remote include`, because listing would need Task to fetch and trust that file,
which is your decision.

## Bind your verbs to your tasks

`meow-gotask bind` prints a `[verbs]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

```toml
[verbs]
test = "task --force test"
# lint: task lint is blocked: ignores errors
```

It binds a verb only to the task of exactly its name, and only a task that
carries no block. Every binding runs the task with `--force`, which runs its
dependencies too, so a pass is never a skip. A verb whose task is `internal`
reads as internal, not as missing.

`meow-gotask check` reads your profile's `[verbs]`, finds each `task <name>`
in a verb's command, and reports every block on that task, a task it can't
find, and a task that can skip run without `--force`. It also reports each
remote include in your Taskfiles, whether or not a verb uses it. It exits 0 on
no finding, 1 on a finding and 3 when it can't read the profile or Task.

## What it reports instead of a list

`check` reads the profile, so it prints the profile's state,
`profile: absent`, `profile: unparseable` or `profile: parsed`, and
`unknown key: <path>` for each key no unit reads, which changes no exit
status.

No command ever reports a state it couldn't read as an empty list; each exits
3 with one of these:

| Line                                                   | Means                                                               |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| `unresolved: not a Task repository`                    | No Taskfile at the root; Task didn't run                            |
| `unresolved: task not found`                           | `task` isn't on `PATH`                                              |
| `unresolved: <file> doesn't parse`                     | A Taskfile isn't valid YAML                                         |
| `unresolved: remote include`                           | A Taskfile includes a remote one, named above it                    |
| `unresolved: a remote Taskfile this listing can't see` | Task refused with 104 or 106 for an include the program didn't find |
| `unresolved: environment: ...`                         | Your Task is older than 3.53.1, the version the unit was tested on  |
| `unresolved: meow-gotask defect: ...`                  | Task rejected a flag this unit passes; report it                    |
| `unresolved: unrecognised shape: ...`                  | Task printed a listing this unit can't read                         |
| `unresolved: task failed ...`                          | Task failed another way; its last lines follow                      |

## What it costs you

The skill's description stays in context on every turn, within the 380
characters the unit's budget states. The program is a native binary shipped
inside the unit, and needs Task and git on the machine. On a machine the unit
carries no binary for, it reports the repository as unresolved and exits 3.

## What it needs

Claude Code 2.1.280 or later, the version this unit was tested on, declared in
`plugins/meow-gotask/requires.toml`; Task 3.53.1 or later; and git.
