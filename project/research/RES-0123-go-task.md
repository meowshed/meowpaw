---
id: RES-0123
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0005
---

# go-task

## Summary

Task declares more about each task than the other runners do, and four of those
declarations change what a green result means. A satisfied status check skips
the task while reporting success. The freshness method decides how that is
judged. Required variables fail for reasons that are neither code nor tool, and
an ignore-error flag swallows the failure the verb was meant to report. Its
task definitions may also come over the network, which makes trust a question
before resolution is.

Research for one supported tool. Task is a task runner written in Go, and the
one in this survey whose task definitions may come over the network, which
gives a pack a trust question to answer before a resolution question.

It covers what marks a Task project, how tasks are declared and enumerated, and
what its freshness and precondition mechanisms mean for a report. It also
covers how remote Taskfiles are trusted, what the pack authors, and what the
skill has to contain.

It does not cover the class of task runners, which is
[RES-0121-task-runners.md](RES-0121-task-runners.md).

## The question

Task declares more about each task than the other runners do: preconditions,
status checks, required variables, platform restrictions, freshness by checksum
or timestamp. Every one of those changes what a green result means.

So the question is which of those declarations a pack must read before it may
report a verb as passing.

## Method

We fetched and read the vendor documentation on 2026-09-20. The guide gave file
discovery, variables, dependencies and the status-against-precondition
distinction. The schema reference gave the full field list and the freshness
methods, and the remote-task material gave the trust prompt, its exit code, the
checksum warning and the flags around it.

One page was reached through a search rather than directly, because the
documentation's own link for it does not resolve; the facts taken from it are
consistent with the command reference read separately.

Nothing was installed or run.

## Findings

### Eight file names, a directory walk, and a global location

Task searches for `Taskfile.yml`, `taskfile.yml`, the `.yaml` variants, and the
`.dist` forms of each, which exist so a committed default can be overridden by
an ignored local file. It walks up the directory tree when it does not find
one, which the guide compares to how Git finds a repository.

A task may also come from the user's global Taskfile with `-g`, or from a
remote source over HTTP or Git.

So, as with mise, **the task a pack sees is not necessarily the repository's**.
The directory walk alone means a Taskfile above the repository root can supply
it, and the global flag and remote includes go further.

### Remote Taskfiles are trusted per source, and the trust is remembered

This is the mechanism a harness has to understand before it enumerates
anything.

On first running a task from a remote Taskfile, Task prints a warning and asks
for confirmation that the source is trusted. Declining exits with code **104**
and nothing runs; accepting means later calls do not prompt.

Task stores a checksum of the remote file, and _"if the checksum changes, Task
prints a warning to inform you that the contents of the remote file has
changed"_. A trusted-hosts list bypasses the prompt both on first download and
when a checksum changes.

The flags that go with it: `--download` forces a fetch and ignores the cache,
`--offline` refuses to fetch, `--cache-wipe` clears cached files and checksums,
and the cache directory and expiry are configurable.

The documentation's own advice is blunt and is quoted as written:

> Never run remote Taskfiles from sources that you do not trust.

For a pack three rules follow. **A remote include is reported before the task
list is used**, because that list is not something the repository contains.
The harness does not accept the trust prompt, for the same reason it does
not run `mise trust`: accepting authorises a third party's code to run in the
user's environment. And **an exit code of 104 is reported as untrusted**,
distinctly from a failure, because they look alike and mean opposite things.

`--offline` is the setting a cautious harness prefers when it only wants to
know what the repository declares locally.

### The task schema declares a great deal, and four fields change what a pass means

The fields available on a task: `cmds` and `cmd`, `deps`, `desc`, `summary`,
`aliases`, `sources`, `generates`, `status`, `use_gitignore`, `preconditions`,
`requires`, `if`, `vars`, `env`, `dotenv`, `dir`, `platforms`, `method`, `run`,
`watch`, `timeout`, `silent`, `ignore_error`, `set` and `shopt`.

Four of them are load-bearing for a report.

`status` against `preconditions`. Both are shell commands whose exit status
decides something, and they decide different things. A satisfied `status` means
the task is up to date and is skipped, while dependents continue. A failed
`precondition` stops the task _and_ its dependents.

So a task with a `status` reports success without running. A pack that does not
separate _skipped as up to date_ from _ran and passed_ is citing evidence for
work that never happened. This is the same finding as mise's freshness cache,
expressed as a shell command instead of a file comparison, which makes it
harder to detect and more important to state.

`method` selects how freshness is judged: `checksum` by default,
`timestamp`, or `none` to skip the check. A project on `timestamp` in a
checkout - where every file has the checkout's modification time - has
freshness behaviour that is an artifact of how the clone was made.

`requires` declares variables a task must have, optionally constrained to
an enumerated set. A verb bound to a task with unmet requirements fails for a
reason that is neither the code nor the tool, and the pack can read the
requirement rather than discovering it.

`ignore_error` means a failing command does not fail the task. A verb bound to
such a task cannot report a failure it was told to ignore, which the pack says
out loud, because the exit status will not.

### Dependencies run in parallel by default, which is a correctness constraint

`deps` run in parallel, so _"dependencies of a task should not depend one
another"_. Serial ordering is expressed by calling tasks from `cmds` instead.

A pack that reads a `deps` list as an ordering has read it wrong, and a project
whose deps do depend on each other has a latent defect that passes most of the
time.

### Variables have a precedence order, and secrets have a marking that is not protection

Variables may be strings, booleans, integers, floats, arrays or maps, defined
globally, per task, or at call time, with dynamic values from shell commands
through `sh:`. The precedence, highest first: task-level declarations, call-time
overrides, included Taskfile variables, global variables, environment
variables.

A variable marked `secret: true` is masked in logs as `*****`, and the
documentation says plainly that this _"is not a substitute for proper secret
management practices."_

That sentence is the one a pack carries. Masking changes what appears in
output; it does not change what the process received, and a harness that treats
a masked variable as safe to capture has misread the guarantee.

### Enumeration is exact, and includes make it namespaced

`task --list` shows tasks with descriptions and `--list-all` includes those
without, and `--json` _"Output task information in JSON format (use with
--list or --list-all)."_

Includes bring other Taskfiles in under a namespace, with support for
operating-system variants, optional includes and flattening. So an enumerated
name may be `docker:build` rather than `build`, and a pack matching bare verb
names against a namespaced list finds nothing.

### What the pack authors

`Taskfile.yml` - tasks, `deps`, `sources` and `generates`, `requires` - and
`.env` files where the project uses `dotenv`.

It does not author a remote include, because adding one makes the project
depend on a third party at run time and that is a decision with a security
consequence rather than a convenience.

### What a reviewer needs that no command reports

Whether `sources` and `generates` are complete, since an incomplete list
produces a task skipped when it should have run.

Whether `status` is checking the right thing, because a `status` that is
accidentally always satisfied makes a task that never runs and never fails.

Whether `deps` that appear ordered actually are, given that they run in
parallel.

Whether `ignore_error` is hiding a failure somebody meant to fix.

Whether a remote include points at a source the project actually controls.

### What the skill has to contain

In the body, in this order:

1. Provenance, first. The eight file names, the directory walk, the global
   Taskfile and remote includes, and that the enumerated list may not be the
   repository's.
2. Trust. The prompt, exit code 104, the checksum warning, trusted hosts,
   and that the harness neither accepts the prompt nor adds a trusted host.
3. Enumeration. `task --list-all --json`, and that names may be
   namespaced by includes.
4. What changes a pass. `status` skipping, `method` choosing how freshness
   is judged, `requires` failing for missing variables, `ignore_error` hiding
   failures.
5. What must never happen. Accepting a trust prompt. Reporting a skipped
   task as passed. Reading `deps` as an ordering. Treating a masked secret as
   protected.

In supporting files: the full task schema; the precondition and status
comparison; the variable precedence order; the remote-Taskfile flags; and the
dated facts with what to re-check.

## Conclusions

1. A Task project is marked by one of eight file names, including the
   `.dist` variants that exist so a committed default can be overridden
   locally.
2. The enumerated task list is reported as resolved rather than declared,
   since Task walks up the directory tree and may also read a global Taskfile
   or a remote source.
3. A remote include is reported before the task list is used, because those
   tasks are not something the repository contains.
4. The harness does not accept a trust prompt and does not add a trusted
   host, because doing so authorises a third party's code to run in the
   user's environment.
5. Exit code 104 is reported as untrusted rather than as a failure, since
   the two look alike and mean opposite things.
6. `--offline` is preferred where the pack only needs what the repository
   declares locally.
7. A checksum-change warning is surfaced, because a remote Taskfile whose
   contents changed is a supply-chain event rather than a diff.
8. Tasks are enumerated with `task --list-all --json`, and matching allows
   for namespaced names introduced by includes.
9. A task skipped by a satisfied `status` is reported as skipped, never as
   passed, and is not cited as evidence.
10. The freshness `method` is read and reported. `timestamp` in a fresh
    checkout behaves as an artifact of the clone rather than of the work.
11. `requires` is read before invocation, so a missing variable is reported
    as a missing input rather than as a failure of the code.
12. `ignore_error` is reported, because a verb bound to such a task cannot
    report the failure it was told to ignore.
13. `deps` are not read as an ordering, since they run in parallel and the
    documentation states dependencies should not depend on one another.
14. A masked secret is not treated as protected, because the documentation
    states masking is not a substitute for secret management.
15. The pack does not author a remote include, since it makes the project
    depend on a third party at run time.
16. The skill body carries provenance, trust, enumeration, what changes a
    pass, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [Task, the guide](https://taskfile.dev/docs/guide) - the eight accepted file
  names and the purpose of the `.dist` variants; the directory walk compared to
  Git's; running from a global Taskfile with `-g` or from a remote source over
  HTTP or Git, with the instruction never to run remote Taskfiles from
  untrusted sources; variable kinds and the precedence order from task-level
  declarations down to environment variables; `secret: true` masking values in
  logs as `*****` with the statement that it is not a substitute for proper
  secret management; `deps` running in parallel with the consequence that they
  should not depend on one another; `status` skipping a task while dependents
  continue against `preconditions` stopping the task and its dependents; `if`
  for conditional execution; `--watch` requiring `sources`; and the interleaved,
  group and prefixed output modes.
- [Taskfile schema reference](https://taskfile.dev/reference/schema) - the task
  fields including `sources`, `generates`, `status`, `use_gitignore`,
  `preconditions`, `requires`, `if`, `dotenv`, `platforms`, `method`, `run`,
  `timeout`, `silent`, `ignore_error`, `set` and `shopt`; the `method` values
  `checksum` as the default, `timestamp` and `none`; and `requires` with an
  optional `enum` constraint.
- [Remote Taskfiles](https://taskfile.dev/docs/remote-taskfiles) and
  [the CLI reference](https://taskfile.dev/docs/reference/cli) - the trust
  prompt on first run with exit code 104 when declined and no further prompting
  once accepted; the stored checksum and the warning when a remote file's
  contents change; the trusted-hosts list bypassing both; and `--download`,
  `--offline`, `--cache-wipe`, the cache directory and the expiry setting.
- [Remote Taskfiles experiment](https://taskfile.dev/docs/experiments/remote-taskfiles)
  - that the experiment was released in version 3.51.1 and is no longer
    experimental.
