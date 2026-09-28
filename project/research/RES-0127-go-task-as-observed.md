---
id: RES-0127
artifact: research
status: approved
revised: 2026-09-27
elaborates: RES-0123
---

# go-task, as observed

## Summary

What Task 3.53.1 does when a program asks it about a repository, observed on
scratch repositories rather than read. The finding that matters most corrects
an assumption RES-0123 makes: listing the tasks is not a read. `task
--list-all --json` writes a checksum into the repository's `.task/` directory
for every task with `sources`, and the next run of that task then skips it as
up to date, although it never ran. Pointing `TASK_TEMP_DIR` outside the
repository stops both. The listing also leaves out every field that changes
what a pass means, so a pack has to read those from the Taskfile itself.

It amends four of RES-0123's conclusions. Conclusion 8's listing writes, so
it needs `TASK_TEMP_DIR`. Conclusion 6's `--offline` then finds no cache,
since the cache moves with that directory. Conclusion 7's checksum warning
never reaches a program without a terminal. And conclusion 9's report of a
skip rests on a line a Taskfile's own `silent: true` removes.

Research for the go-task pack. It adds observations to
[RES-0123-go-task.md](RES-0123-go-task.md), which read the documentation.

## The question

RES-0123 says what Task documents. A pack parses what Task prints, so the
question is what the machine-readable listing carries, what listing does to the
repository, and how a skipped, confirmed, argument-taking, internal or remote
task behaves when no person is at the terminal.

## Method

I ran Task 3.53.1, installed through Homebrew, on 2026-09-27 in scratch
directories. One held a Taskfile with an include of a local Taskfile, and one
held an include of `https://raw.githubusercontent.com/go-task/task/main/Taskfile.yml`,
the file on Task's `main` branch that day, so a repeat reads whatever that
branch then holds. A local and a remote include were never combined in one
Taskfile, so a remote include reached through a local one wasn't observed.
Standard input was closed on every run, so no prompt could be answered. To see
the checksum warning I trusted the remote Taskfile once, with
`--trusted-hosts`, in a scratch directory nothing else reads, then altered the
stored checksum.

## Findings

### The listing names each task and its file, and nothing that changes a pass

`task --list-all --json` prints one object holding `tasks` and `location`. Each
task carries `name`, `task`, `desc`, `summary`, `aliases`, `up_to_date` and a
`location` with `line`, `column` and `taskfile`, the file declaring it.

It carries no `requires`, `ignore_error`, `prompt`, `status`, `sources`,
`method` or `internal`. A task marked `internal: true` is left out of the
listing entirely. So a pack learns what stops a task running unattended only
by reading the task's own definition in the file `location.taskfile` names.

A task from an included Taskfile lists with its namespace, `sub:inner`, and
`location.taskfile` naming the included file. In a directory holding no
Taskfile, the listing gave the parent directory's tasks, with the parent's file
as their `location.taskfile`.

### Listing writes into the repository, and the write makes a later run skip

Listing a Taskfile whose task `build` declares `sources` and `generates` wrote
`.task/checksum/build` into the directory. It printed nothing to say so.

In two identical directories, `task build` after a listing printed `Task
"build" is up to date` and didn't run. `task build` in the one never listed
ran. So a program that lists the tasks before a verb runs one can make that
verb pass on a run that never happened.

With `TASK_TEMP_DIR` set to a directory outside the repository, the listing
wrote its checksum there, the repository gained no file, and `task build`
afterwards ran. A task on `method: timestamp` wrote `.task/timestamp/<task>`
when listed without it, so the write isn't peculiar to checksums.

`TASK_TEMP_DIR` also moves the remote cache. In the directory where the remote
Taskfile had been trusted, a listing with `TASK_TEMP_DIR` pointing elsewhere
failed with 104, `not trusted by user`, because Task no longer found the
checksum the person's trust had stored.

Listing ran none of the Taskfile's commands. A `status` command that creates a
file left no file, and its task listed with `"up_to_date": false`. A global
variable whose `sh:` creates a file left no file either.

### A task that skips, asks, needs a variable, ignores an error or is internal

Each of these ran with standard input closed:

| Task declares            | Exit status | What Task printed                                                                    |
| ------------------------ | ----------- | ------------------------------------------------------------------------------------ |
| A satisfied `status`     | 0           | `Task "fresh" is up to date`, on standard error, and the command didn't run          |
| The same, with `--force` | 0           | The command's output: it ran                                                         |
| `requires: vars: [ENV]`  | 206         | `cancelled because it is missing required variables: ENV`                            |
| `ignore_error: true`     | 0           | `task: [lint] exit 1`, the failing command's status, and success                     |
| `prompt:`                | 201         | `cancelled because it has a prompt and the environment is not a terminal. Use --yes` |
| `internal: true`         | 202         | `Task "priv" is internal`                                                            |

So a skip and an ignored error both exit 0, and only standard error tells them
from a pass: both the skip line and `task: [lint] exit 1` went to standard
error. With `--silent`, or with `silent: true` on the task or at the top of
the Taskfile, a skipped task printed nothing at all, so the Taskfile itself can
hide the only line that shows a skip.

Three more fields decide whether a task runs, and two of them pass silently:

| Task declares                    | Exit status | What Task printed                   |
| -------------------------------- | ----------- | ----------------------------------- |
| `if: 'false'`                    | 0           | Nothing, and the command didn't run |
| `platforms: [windows]`, on macOS | 0           | Nothing, and the command didn't run |
| `preconditions: ['false']`       | 201         | `precondition not met`              |

With `--force`, the `if` and `platforms` tasks still ran nothing and exited 0,
so forcing doesn't reach them.

`task --force top`, where `top` depends on `dep` and both have a satisfied
`status`, ran both: `--force` forces a task's `deps` too.

An unknown flag to the listing, `--nosuch`, exited 2 and printed the usage
text followed by `unknown flag: --nosuch`.

### A remote include fails the listing without a terminal, whatever the checksum says

A Taskfile including a remote Taskfile gave these, with a fresh home directory
and no terminal:

- `--offline`, with nothing cached: exit 106, `was not found in the cache`.
- Without `--offline`: exit 104, `not trusted by user`, and no prompt.
- With `--trusted-hosts raw.githubusercontent.com`: exit 0, and the listing
  wrote `.task/remote/` and eight `.task/checksum/remote-*` files into the
  directory.
- With that stored checksum then altered, with or without `--download`: exit
  104 and the same `not trusted by user` line.

So without a terminal, a remote Taskfile whose contents changed since it was
trusted fails exactly as one nobody trusted. The checksum warning RES-0123
describes reaches only a person at a terminal, and a program running Task
never sees it.

## Conclusions

1. Tasks are listed with `task --list-all --json` and `TASK_TEMP_DIR` set to
   a directory outside the repository, because listing otherwise writes a
   checksum or timestamp that makes the next run skip a task that never ran.
   The cost is that a listing can see neither the trust a person gave a remote
   Taskfile nor its cache, since both live in the directory the listing no
   longer uses, so a listing with a remote include fails with 104, or with 106
   under `--offline`, whatever the person did.
2. `requires`, `ignore_error`, `prompt`, `internal`, `status`, `sources`,
   `method`, `if`, `platforms` and `silent` are read from the file
   `location.taskfile` names, because the listing carries none of them, and
   `if` and `platforms` make a task exit 0 without running even under
   `--force`.
3. A remote include is found by reading the committed Taskfile and the local
   Taskfiles it includes, before anything is listed, because a listing with
   one fails with 104 or 106 unless something trusts a host, and trusting a
   host is the person's decision (RES-0123).
4. Exit status 104 or 106 from such a listing is reported as a remote
   Taskfile the listing can't see, never as untrusted and never as an empty
   list: untrusted would contradict a person who trusted it, and an empty list reads as a repository that declares
   no tasks, and each verb would then read as unbound where it is blocked.
5. A changed remote checksum can't be told from an untrusted remote Taskfile
   without a terminal, so a program that runs Task unattended can surface
   neither the warning nor the change.
6. A skip can't be read reliably from a run: it exits 0, and `silent: true`
   in the Taskfile hides its line. `--force` runs a skipping task and its
   `deps`, at the cost of running them again each time.
7. `ignore_error` is reported, because the task exits 0 on a failure it was
   told to ignore.
8. A task's `prompt` (exit 201), `internal` (202) and `requires` (206) are
   read from its definition and reported before anything runs, and `--yes` is
   never passed, because the prompt is its author asking for a person.
9. A directory without a Taskfile lists its parent's tasks, which confirms
   RES-0123 conclusion 2: the list is what resolves here, not what the
   repository declares.

## Sources

- Task 3.53.1, observed on 2026-09-27 in the scratch directories the Method
  describes.
- [RES-0123-go-task.md](RES-0123-go-task.md), read 2026-09-27, for what the
  documentation states.
