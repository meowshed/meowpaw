---
id: SPC-1060
artifact: spec
status: live
revised: 2026-10-03
states:
  [
    REQ-0079,
    REQ-1292,
    REQ-1296,
    REQ-1298,
    REQ-1306,
    REQ-1312,
    REQ-1320,
    REQ-1322,
    REQ-1324,
    REQ-1326,
    REQ-1328,
    REQ-2522,
    REQ-2524,
    REQ-2526,
    REQ-2528,
    REQ-2530,
    REQ-2534,
    REQ-2536,
    REQ-2538,
    REQ-2540,
    REQ-2818,
    REQ-2820,
    REQ-2822,
    REQ-3176,
    REQ-2608,
    REQ-2610,
    REQ-2612,
    REQ-2614,
    REQ-2616,
    REQ-2618,
    REQ-2620,
    REQ-2210,
    REQ-1824,
    REQ-1826,
    REQ-1828,
  ]
---

# The git pack

## Scope

This covers `meow-git`, the pack that refuses a commit on the trunk and checks
every commit on a branch before it is pushed. It states the `[git]` table, what
each hook checks, how it finds `meow-scm`, and how it reports.

It leaves the message convention to SPC-1050, which the pack uses through
`meow-scm`, and when a task stacks on another to the method's chain. It states the
restack that rebuilds a stack's branches, and the bounds ADR-2420 sets on a
worktree manager or any other tool that runs source control operations.

ADR-1090 decides it, EPC-1060 realises it, and `meow-git` implements it,
verified under issue 138. ADR-2550 adds the restack, which EPC-2430 realises.

## Boundary

| Surface                             | What it is                                                      |
| ----------------------------------- | --------------------------------------------------------------- |
| `.meowpaw/profile.toml`, `[git]`    | The repository's trunk and whether every commit must be signed  |
| `plugins/meow-git/hooks/hooks.json` | Two `PreToolUse` command hooks, one for commit and one for push |
| `plugins/meow-git/bin/meow-git`     | The program: `commit-guard`, `push-guard` and `restack`         |
| `plugins/meow-git/README.md`        | The pack's documentation page                                   |

## Behaviour

### The `[git]` table

```toml
[git]
trunk = "main"
require_signatures = true
```

`trunk` names the branch nobody commits to directly (REQ-1292).
`require_signatures` says every commit pushed must carry a good signature from
a trusted key (REQ-1326). A key the pack doesn't read is reported as ignored.

### The hooks

Each hook is a `PreToolUse` command hook on the shell tool, matched by an `if`
rule to its own command: `git commit` for the first, `git push` for the
second. Claude Code runs a hook whenever it can't tell which commands a shell
input runs, such as one holding `$()` or `$VAR`, so the rule is a filter and
not a promise. Each guard reads the command from the hook's input and checks
nothing where the command doesn't run `git commit` or `git push`, naming
that. Where the command runs it in another directory, through `cd <dir>` or
`git -C <dir>`, the guard judges that directory's repository and branch, and
it judges the session's directory where the named one doesn't exist. The scan
errs towards finding the command: text that only mentions `git commit` inside
quotes counts. A hook blocks by exiting
with status 2 and writing its reason to standard error, which reaches the model
as the reason the command didn't run. It lets the command through by exiting 0.

### On commit

`commit-guard` blocks when the current branch is the declared trunk, naming the
trunk and saying to take a branch. Where no trunk is declared it blocks
nothing.

### On push

`push-guard` reads every commit the push would publish: each commit reachable
from the current head that no remote-tracking branch already has. For each
one:

- It passes the commit's full message to `meow-scm check-message`. A failure
  blocks the push, naming the commit, its subject and each line `meow-scm`
  reported. Where `meow-scm` isn't found, the hook reports the message check as
  unrun for every commit, and never as passed (REQ-0079).
- Where `require_signatures` is true, it reads the commit's signature verdict
  from the tool. Only a good signature from a trusted key passes (REQ-2530).
  A verdict that the key material is missing locally is reported as
  unverifiable, and one that there is no signature as unsigned. Either blocks,
  and so does every other verdict, each named as the tool gives it.

The report names every failing commit, not only the first, so one push shows
everything to fix.

### Finding `meow-scm`

The pack uses `meow-scm` only where it is installed, and never installs it
(REQ-0079). It looks, in order, at the path in `MEOW_SCM` where set, at
`meow-scm` beside the pack in the same marketplace directory, and at the
newest version of `meow-scm` in the platform's plugin cache.

### The program

The program is the `git` subcommand of the native tool SPC-1080 states,
shipped as a binary inside the pack. Where the pack carries no binary for the
machine, the launcher reports each check as unrun and lets the command
through, because a pack that blocked every commit for a missing binary would
punish the person for something the pack can't check.

### Source-control discipline

Every list of paths the native tool reads from git is NUL-separated with `-z`,
so an unusual path reads as it is (REQ-2522). Every git read goes through one
helper, which sets `GIT_OPTIONAL_LOCKS=0`, and a unit test fails on git started
anywhere else in the native tool (REQ-2524). The harness writes git
configuration only inside the repository, and a unit test fails where the
native tool, a shipped prompt or a workflow names `git config` with `--global`
or `--system` (REQ-2540) (ADR-1570).

The first sign-off names the commit's author, which `meow-scm check-message`
holds where the trailer is required (REQ-1312); a branch name carries no date and no
author, which the push guard holds (REQ-2818); a line added to the record
cites a pull request, never a commit hash, which `paw check frozen`
holds (REQ-3176); and every read of source control runs with prompting,
paging, advice and machine-wide configuration off (REQ-2526, REQ-2528). The
`commit` skill carries the rest: one task, one branch, one pull request and
one squashed commit on the trunk; short-lived branches from the one trunk; no
merge, tag, release or publish without an instruction; one branch in one
working tree, a locked tree with its reason; a grown branch split; a force
push over a reviewed branch disclosed; and every commit signed and signed off
where the repository asks (REQ-1296, REQ-1298, REQ-1306, REQ-1320, REQ-1322,
REQ-1324, REQ-1328, REQ-2534, REQ-2536, REQ-2538, REQ-2820, REQ-2822) (ADR-1320).

Every commit reaching the trunk leaves it building with its checks passing
(REQ-2210): a task lands only as one squashed commit of a pull request whose
gate passed on its branch, the commit guard refuses a commit on the trunk, and
in this repository CI's `gate` job runs `mise run all` on every pull request
and on every push to the trunk.

### Restacking

`meow-git restack <branch>...` rebuilds a stack, given its branches from the
bottom layer up. It rebases each branch onto the one below it, the first onto
the trunk, in that order, and a branch whose base hasn't moved is left as it
is. Where `require_signatures` is true, the rebase signs every commit it writes
again (REQ-2614). It pushes nothing. For each branch it updated, it prints
`updated: <branch>` and the push that publishes it,
`git push --force-with-lease=<branch>:<revision> origin <branch>`, where
`<revision>` is the remote-tracking revision it read before rewriting, so a
force push replaces only the revision last seen (REQ-1828).

A conflict stops the restack at that branch: it aborts the rebase, so neither
side is discarded, prints `conflict: <branch>` with the files in conflict, and
exits 1 (REQ-1826). Wherever it stops, it prints `updated:` for each branch it
rewrote and `not updated:` for each it didn't reach, and it never runs again on
its own to cover the gap (REQ-1824). A branch with uncommitted changes in its
working tree, or checked out in another one, stops it before it rewrites
anything (REQ-2534).

### Tools that run operations

Where a tool such as a worktree manager documents no machine-readable output,
the harness uses it only to run an operation, and reads the state that results
from git (REQ-2608). The harness calls no command that writes a message,
commits, rebases and removes a working tree in one go, such as worktrunk's
merge, and the `commit` skill lists each such command it never runs
(REQ-2610). Every commit message the harness uses is written by the `commit`
skill and passes `meow-scm check-message`, and a message a tool generated is
never used (REQ-2612). Where `require_signatures` is true, the harness uses no
workflow that rebases on its own, and a rebase after signing is a change the
harness signs again (REQ-2614). A summary a model wrote is never cited as
evidence, and appears only where a person reads a list (REQ-2616).

The harness removes a working tree only in the foreground, when the person or
the step that made it asks, and never from a background job (REQ-2618). Where
working trees share files, they share only ignored build output and never
tracked source, and the harness reports a filesystem that can't share it
(REQ-2620). The `commit` skill carries these rules beside its rules for one
branch in one working tree.

## Failure paths

| Condition                               | What happens                                                                        |
| --------------------------------------- | ----------------------------------------------------------------------------------- |
| No profile or no `[git]` table          | Commit: nothing blocked. Push: messages checked; trunk and signing undeclared       |
| A commit on the declared trunk          | Blocked, exit 2, naming the trunk                                                   |
| A message `meow-scm` fails              | The push is blocked, naming the commit and each failure                             |
| `meow-scm` not found                    | The message check is reported unrun for every commit; the push isn't blocked on it  |
| An unsigned commit, signatures required | The push is blocked, naming the commit as unsigned                                  |
| Key material missing locally            | The push is blocked, naming the commit as unverifiable                              |
| Nothing to publish                      | The push goes through, and the hook says it checked no commits                      |
| A conflict during `restack`             | The rebase is aborted, the branch and its files named, the rest not updated, exit 1 |
| A `restack` branch with local changes   | Nothing is rewritten; the branch is named, exit 1                                   |
| No binary for the machine's target      | Every check reported unrun, and nothing blocked                                     |
