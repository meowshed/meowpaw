---
id: ADR-1090
artifact: adr
status: draft
revised: 2026-09-26
addresses: [REQ-0079, REQ-1292, REQ-1326, REQ-2530]
supersedes: []
---

# 1090. A `git` pack refuses a commit on the trunk and checks a branch before it is pushed

## Decision

A new pack, `meow-git`, carries what `meow-scm` leaves to a tool: it refuses a
commit on the trunk, and it checks every commit on a branch before the branch
is pushed. It carries two `PreToolUse` command hooks, each matched by an `if`
rule so that it runs only for its own command.

On `git commit`, the hook blocks when the current branch is the trunk the
repository declares (REQ-1292):

```toml
[git]
trunk = "main"
require_signatures = true
```

On `git push`, the hook reads every commit the push would add to the trunk and
blocks when any of them fails, naming the commit and the reason:

- the message fails `meow-scm check-message`, where `meow-scm` is installed.
  Where it isn't, the hook reports the message check as unrun and lets the push
  through on the other checks, because REQ-0079 lets a unit use another's
  program only if it says so when the other is absent.
- the repository sets `require_signatures`, and the commit's verdict is
  anything but a good signature from a trusted key (REQ-1326, REQ-2530). A
  verdict that says the key material is missing locally is reported as
  unverifiable, never as unsigned.

The push is the enforcement point, not the commit. A command hook sees the
command's text, and reading a message out of an arbitrary shell command, with
its quoting, heredocs and files, would misread some of them. At the push the
commits exist and the tool itself reports each message and each signature, so
the hook reads facts and not a command line. A commit that fails can still be
amended on the branch, and nothing leaves the machine until every commit
passes.

REQ-0079 enters in this record: a unit outside the kernel may use another
unit's program when it is installed, and reports the check as unrun when it
isn't. The pack finds `meow-scm` among the units installed beside it and never
installs it.

Where the profile declares no `[git]` table, the hook refuses nothing on commit
and checks only the messages at push, and says the trunk and the signature
policy are undeclared.

## Why

ADR-1080 records that the message check runs only because the skill tells the
model to run it, which is weaker than a hook, and it names this pack as where
the hook lives, since the hook matches a tool's command. The trunk and
signatures are the two rules this repository's constitution states and nothing
enforces: a commit on `main` and an unsigned commit both reach review today
only if nobody slips.

## Alternatives

| Option                                              | Better at                               | Why it lost                                                                                                                                      |
| --------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Check at push, from the commits the tool reports    | Reading facts, never a command line     | Chosen                                                                                                                                           |
| Check the message at `git commit`, from the command | Catching a bad message before it exists | The message has to be read out of shell quoting, heredocs and files, and some would be misread                                                   |
| Install the repository's own commit-msg hook        | Running whatever starts the commit      | It writes a control file into the repository for every user, which REQ-2540 allows only when committed, and the file would carry the pack's code |
| Copy the message check into the pack                | Working with `meow-scm` absent          | Two copies of one check drift, which REQ-0079 exists to avoid                                                                                    |
| Leave enforcement to the skill                      | Costing nothing                         | A rule enforced by a model remembering it is the rule RES-0224 found broken by being forgotten                                                   |

## What it costs

Two command hooks, each run only on its own command, so the rest of a session
pays nothing. The hooks use the interpreter the other units already depend on,
and where it is missing they report every check as unrun and block nothing,
which the pack's page says.

A push takes as long as its checks: one message check and one signature
verdict per commit.

The pack names `meow-scm`, which REQ-0079 now allows.

## What would reverse it

- A measurement shows commits reaching the trunk that the push hook should
  have stopped. The enforcement point would then move, to the commit or to the
  forge.
- The platform gives a hook the commit's message before the commit is made.
  The message check would then move to the commit.

## Consequences

- `plugins/meow-git/` carries the hooks, the program they run, a manifest, a
  budget of 0 characters and a documentation page, and the marketplace lists
  it.
- REQ-0079 is approved with this record, and a specification for the pack
  states the `[git]` table and what each hook checks.
- This repository declares `trunk = "main"` and `require_signatures = true`.

## How I will know it was realised

1. A `git commit` on the declared trunk is blocked, naming the trunk, and one on
   another branch runs.
2. A push that would add a commit whose message fails `meow-scm check-message`
   is blocked, naming the commit and the failure.
3. With `meow-scm` absent, the push hook reports the message check as unrun and
   doesn't claim it passed.
4. With `require_signatures`, a push adding an unsigned commit is blocked, and
   a commit whose key material is missing locally is reported as unverifiable.
5. With no `[git]` table, nothing is refused on commit, and the push checks
   messages and says the trunk and the policy are undeclared.

Each is a fixture over a scratch repository, and none needs a model.

## What this does not settle

- Worktrees, stacked branches and the squash merge.
- Enforcement on the forge, which runs whatever happened on the machine.
- Version control tools other than `git`, which would each need a pack.
