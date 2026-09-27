---
id: RES-0126
artifact: research
status: approved
revised: 2026-09-27
elaborates: RES-0122
---

# mise, as observed

## Summary

What mise 2026.9.11 does when a program asks it about a repository, observed
on a scratch repository rather than read. Three findings change what a pack
can rely on. The machine-readable task list leaves out the `confirm` field, so
a task that asks for a person can be told apart only from its own file. A
task listed from `mise.local.toml` replaces the repository's task of the same
name, and the listing shows it as an ordinary task. A task skipped as fresh
exits 0, and `--force` stops the skip. One finding corrects RES-0122: an
untrusted file holding plain tasks lists them, so a listing is no evidence
that a configuration is trusted.

Research for the mise pack. It adds observations to
[RES-0122-mise.md](RES-0122-mise.md), which read the documentation, and it
repeats nothing that document states.

## The question

RES-0122 says what mise documents. A pack parses what mise prints, so the
question is what the machine-readable output carries, what an untrusted
configuration does to it, and how a skipped, confirmed or argument-taking task
behaves when no person is at the terminal.

## Method

I ran mise 2026.9.11 (macos-arm64, built 2026-09-17) on 2026-09-27 in two
scratch git repositories, one with a parent directory holding its own
`mise.toml`. Every command ran with standard input closed where a prompt was
possible. Nothing was trusted: every configuration stayed untrusted, and
`mise trust --show` confirmed it before and after.

## Findings

### The task list carries these fields, and `confirm` isn't one of them

`mise tasks ls --json` prints a JSON array with one object per task, holding
`name`, `aliases`, `description`, `source`, `config_sources`, `depends`,
`depends_post`, `wait_for`, `env`, `dir`, `hide`, `global`, `raw`,
`interactive`, `sources`, `outputs`, `shell`, `quiet`, `silent`, `tools`,
`usage`, `timeout`, `run`, `args` and `file`.

A task declared with `confirm = "Are you sure?"` lists with no field that
says so, and `mise tasks info <name> --json` omits it too. A file task whose
header line reads `#MISE confirm="Really?"` lists the same way, with no field
naming the prompt, and mise honoured the header when the task ran. So a pack
learns that a task asks for a person only by reading the task's own
definition: the `confirm` key of a TOML task, or the `#MISE confirm=` line of
a file task.

A hidden task, `hide = true`, is left out of the list unless `--hidden` is
passed, and listed with `"hide": true` when it is.

A file task, an executable under `mise-tasks/`, lists beside the TOML tasks
with `file` set to its path, which confirms RES-0122's point that parsing
`mise.toml` alone misses it.

File tasks list from five directories at the repository's root, with or
without a configuration file beside them: `mise-tasks/`, `.mise-tasks/`,
`mise/tasks/`, `.mise/tasks/` and `.config/mise/tasks/`. Two file tasks of one
name in two of them list once, from `mise/tasks/` over `mise-tasks/`, with
nothing marking the other.

### A task's arguments are readable without running it

A task declaring `usage = 'arg "<name>"'` lists with `usage` holding that
string. `mise tasks info <name> --json` returns a `usage_spec` whose
`cmd.args` lists each argument with `name` and `required`, here
`"required": true`. Running the task bare fails before its command starts,
with `Missing required arg: <name>`.

### A confirm task fails when nobody can answer

`mise run deploy`, the TOML task, and `mise run ship`, the file task, each
with standard input closed, printed
`task requires confirmation but there was nobody to ask; pass --yes to
accept` and `task failed`. So mise doesn't run either task unattended, and the
flag that would run it, `--yes`, is the one a program must not pass.

### An untrusted configuration lists simple tasks and fails on a template

`mise trust --show` prints one line per configuration directory, the path
followed by `: untrusted` or `: trusted`, and changes nothing.

An untrusted `mise.toml` holding plain tasks listed them. RES-0122's source
says a file holding only plain tasks needs no trust, and this matches it, but
RES-0122's own summary says an untrusted configuration yields nothing, and in
2026.9.11 that holds only for a file holding a template. So a clean exit with
a task list says nothing about trust, and only `mise trust --show` does. An
untrusted `mise.toml` holding a template, `{{exec(command="echo x")}}`, made
`mise tasks ls --json` exit 1, print nothing on standard output, and print
`Config files in <path> are not trusted` on standard error. So an untrusted
configuration can look like a project with no tasks only to a program that
ignores the exit status and standard error.

### A task can come from outside the repository, and one can replace another

With a parent directory declaring `extra` and `test`, and the repository
declaring `test`:

- `extra` listed with `source` set to the parent's `mise.toml`, outside the
  repository.
- `test` listed with `source` set to the repository's `mise.toml`, so the
  nearer file won.

Adding an uncommitted `mise.local.toml` that also declares `test` changed the
listing: `test` now carried `source` and `config_sources` naming
`mise.local.toml` alone, and `mise run test` ran the local command. Nothing in
the listing marked the repository's own `test` as replaced. A pack sees the
replacement only by comparing the source it lists with the files the
repository commits.

### A skipped task exits 0, and `--force` stops the skip

A task declaring `sources = ["a.txt"]` and `outputs = ["b.txt"]` printed
`[test] sources up-to-date, skipping` on standard error and exited 0 when
`b.txt` was newer than `a.txt`. So only that line tells a skip from a run. `mise run --force test` ran the command. After the content of
`a.txt` changed while its time was set back, the task ran, so this version
decides freshness by more than the file times RES-0122's source describes. The
listing doesn't say which method decides.

### The listing names each configuration file, and the version is on every error

`mise config ls --json` lists each configuration file mise read as `path`,
with the tools it declares, the user's own configuration included. Every
error mise printed ended with the version line, `Version: 2026.9.11
macos-arm64 (2026-09-17)`, and an unknown flag to `tasks ls` failed with
`error: unexpected argument`. `mise settings get
idiomatic_version_file_enable_tools` printed `[]`, the default that leaves
every idiomatic version file unread.

## Conclusions

1. `confirm` is read from the task's own definition, the TOML key or the
   file task's `#MISE confirm=` line, because the machine-readable output
   omits it. Only a definition in a file the pack can read is read this way,
   so a task from another file carries an unknown `confirm`. Running the task
   with standard input closed would find `confirm` in any file, from mise's
   refusal, but only by trying to run it, and a pack deciding whether to bind
   a task has to know before anything runs.
2. Required arguments are read from `mise tasks info <name> --json`, in
   `usage_spec.cmd.args[].required`, without running the task.
3. `--yes` is never passed, since it is the flag that runs a confirm task
   without a person.
4. An enumeration that exits non-zero is never read as an empty list,
   because an untrusted configuration holding a template prints nothing and
   exits 1. Standard error saying `not trusted` marks it as untrusted in
   2026.9.11, and a pack's fixtures running real mise check that text again
   on each run.
5. A listed task whose `source` is not a file the repository commits is
   reported with that source, and a task the repository commits whose listed
   source is another file is reported as replaced, because the listing marks
   neither.
6. A skipped task can't be told from a passed one by its exit status, only by
   the line mise prints, and `--force` stops the skip at the cost of running
   a fresh task again.
7. An `unexpected argument` from mise is reported as an unsupported flag,
   with the version line. Only an unknown flag was observed; that a flag
   from a later release fails the same way is inferred, and either way the
   error can't tell the two apart.
8. A mise repository is detected by its configuration files and by any of
   the five task directories, because a repository holding only file tasks
   has no configuration file.
9. The configuration files mise loads are listed by
   `mise config ls --json`, the user's own among them, and an idiomatic
   version file is unread unless `idiomatic_version_file_enable_tools` names
   its tool, which it doesn't by default.

## Sources

- mise 2026.9.11, observed on 2026-09-27 in the scratch repositories the
  Method describes.
- [RES-0122-mise.md](RES-0122-mise.md), read 2026-09-27, for what the
  documentation states.
