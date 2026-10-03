---
id: TSK-4310
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2320
closes: [REQ-2944, REQ-2946]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Read a personal profile, write it with `meow-checks local`, and refuse a machine path in it

The tool reads `.meowpaw/profile.local.toml` after the shared profile and lets
its `[verbs]` replace the shared ones on that machine, `meow-checks local`
writes it and excludes it through `.git/info/exclude`, and a personal verb
that names a path on this machine stays unresolved, as SPC-1080 and SPC-1040
state. One task, one branch, one pull request, one review: the tests first,
then the change, its documentation and its marks.

## Acceptance criteria

1. Given a git fixture with no personal profile, when
   `meow-checks local test "mise run test"` runs, then
   `.meowpaw/profile.local.toml` holds `test = "mise run test"` under
   `[verbs]`, `.git/info/exclude` holds `/.meowpaw/profile.local.toml`, and
   `git status --porcelain` prints nothing (REQ-2944). Closed by: a crate test
   naming REQ-2944, seen failing first.
2. Given that fixture after a second `local` call, when a test reads
   `.git/info/exclude`, then the line appears once (REQ-2944). Closed by: a
   crate test naming REQ-2944.
3. Given a shared `test = "true"` and a personal `test = "false"`, when
   `meow-checks status` runs, then `test` resolves to `false` and names
   `.meowpaw/profile.local.toml` as its file. Closed by: a crate test.
4. Given a personal `test = "/Users/someone/bin/runner"`, when
   `meow-checks run test` runs, then `test` is unresolved of the kind
   `machine path`, the report names the path, nothing runs and the exit
   status is 3; the same value in the shared profile resolves (REQ-2946).
   Closed by: a crate test naming REQ-2946.
5. Given a personal profile holding a `[commits]` table, when
   `meow-checks status` runs, then it names `commits` as an unknown key.
   Closed by: a crate test.
6. Given a directory that isn't a git working tree, when `meow-checks local
test "true"` runs, then it writes nothing and exits 1. Closed by: a crate
   test.

## What to do

Add the personal profile to the reader in `crates/meow/src/profile.rs`, with
`[verbs]` its only known table, and the subcommand `local <verb> <command>` to
the `verbs` feature. I chose that name for the command that creates the file,
because ADR-2370 says the tool creates it and names no command. The command
writes only the personal file and `.git/info/exclude`, both outside what the
repository keeps (REQ-1563).

Name the source file beside every resolved verb in `status`, `run` and
`status --json`. Add the kind `machine path` to the unresolved kinds, and
apply it only to a verb read from the personal file.

Update `plugins/meow-checks/README.md` with the personal file, the `local`
command and the new kind.

## Depends on

- TSK-4300 (blocking): the personal file's other tables are named through its unknown-key list.

## Evidence

Not yet.

## Left alone

A personal setting outside `[verbs]`, because ADR-2370 confines the personal
file to verbs. The shared profile's own commands, which the machine-path rule
doesn't reach.
