---
id: SPC-1060
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#138"
states: [REQ-0079, REQ-1292, REQ-1326, REQ-2530]
---

# The git pack

## Scope

This covers `meow-git`, the pack that refuses a commit on the trunk and checks
every commit on a branch before it is pushed. It states the `[git]` table, what
each hook checks, how it finds `meow-scm`, and how it reports.

It leaves the message convention to SPC-1050, which the pack uses through
`meow-scm`, and worktrees, stacked branches and the squash merge to later
decisions, which ADR-1090 names.

ADR-1090 decides it, EPC-1060 realises it, and `meow-git` implements it,
verified under issue 138.

## Boundary

| Surface                             | What it is                                                      |
| ----------------------------------- | --------------------------------------------------------------- |
| `.meowpaw/profile.toml`, `[git]`    | The repository's trunk and whether every commit must be signed  |
| `plugins/meow-git/hooks/hooks.json` | Two `PreToolUse` command hooks, one for commit and one for push |
| `plugins/meow-git/bin/meow-git`     | The program the hooks run: `commit-guard` and `push-guard`      |
| `docs/meow-git.md`                  | The pack's documentation page                                   |

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
rule to its own command, so it runs for that command and for no other:
`git commit` for the first, `git push` for the second. A hook blocks by exiting
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

## Failure paths

| Condition                               | What happens                                                                       |
| --------------------------------------- | ---------------------------------------------------------------------------------- |
| No profile or no `[git]` table          | Commit: nothing blocked. Push: messages checked; trunk and signing undeclared      |
| A commit on the declared trunk          | Blocked, exit 2, naming the trunk                                                  |
| A message `meow-scm` fails              | The push is blocked, naming the commit and each failure                            |
| `meow-scm` not found                    | The message check is reported unrun for every commit; the push isn't blocked on it |
| An unsigned commit, signatures required | The push is blocked, naming the commit as unsigned                                 |
| Key material missing locally            | The push is blocked, naming the commit as unverifiable                             |
| Nothing to publish                      | The push goes through, and the hook says it checked no commits                     |
| No binary for the machine's target      | Every check reported unrun, and nothing blocked                                    |
