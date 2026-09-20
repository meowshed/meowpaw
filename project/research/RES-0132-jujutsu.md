---
id: RES-0132
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0131, RES-0005
---

# Jujutsu

## Summary

Jujutsu stores its history in a git repository, which makes it supportable as
an alternative front end and hides where the two disagree. Every command
snapshots the working copy, so there is no read-only invocation and running
status has already committed what changed. Several git features are
unimplemented, and three of them matter here: hooks do not run,
attribute files have no effect, and annotated - therefore signed - tags cannot
be made.

Research for one supported tool. Jujutsu is a version control system that uses
a Git repository as its storage, so a harness supports it as an alternative
front end and never as a second world. That storage also hides several places
where the two disagree.

It covers what marks a Jujutsu workspace, what it does to the working copy on
every command, and which Git features it does not support. It also covers how
signing works, how to get machine-readable output, what the pack authors, and
what the skill has to contain.

It does not cover git itself, which is [RES-0131-git.md](RES-0131-git.md).

## The question

A harness that supports both has to know exactly where the abstraction leaks.
The answer is in two places. In the working copy, which Jujutsu writes to
whenever anything invokes it, and in a list of Git features it does not
implement, several of which this method depends on.

## Method

We fetched and read the vendor documentation on 2026-09-20. The
git-compatibility page gave the colocated default and the unsupported and
partially supported lists, and the working-copy page gave the snapshot model
and the operation log. The configuration page gave the signing behaviours and
the verification default, and the template page gave machine-readable output.

The unsupported list was read in full rather than sampled, because the
consequences for this method come from three specific entries in it.

Nothing was installed or run.

## Findings

### Colocation is the default, and it is what makes support feasible

A colocated workspace shares one working copy between Git and Jujutsu, and the
documentation states it is _"the default for Git-backed workspace created with
`jj git init` or `jj git clone`."_

Interoperation is automatic: _"Jujutsu will import and export from and to the
Git repo on every `jj` command automatically."_ Mixing the two is supported,
and the recommendation is to keep Git commands read-only and make changes
through Jujutsu.

So a harness can read a colocated repository with git and write to it with
Jujutsu, and the two will agree. That is the property the whole support story
rests on.

### Every command snapshots the working copy, which makes reading an action

The working copy has no staging area: _"Most `jj` commands you run will commit
the working-copy changes if they have changed."_ Tracking is implicit, so a new
file is included automatically and a deleted file is removed automatically.

Each command runs three steps: snapshot the working copy as an operation,
create commits in memory, update the working copy.

For a harness this is the central finding. **Running `jj status` to see what
changed has already committed what changed.** It offers no read-only invocation
the way git does, so the mental model of `status` as an inspection fails here.

Two consequences. A harness inspecting a Jujutsu workspace should prefer git's
read-only commands, which is what the documentation recommends anyway. And any
Jujutsu command the harness does run is recorded in the operation log, which is
recoverable - `jj undo` and the operation log exist precisely because every
command is a change.

The operation log is the compensating strength. Every command is recoverable,
which is a stronger guarantee than git offers, and it means a mistake by the
harness is undoable in a way a `git reset --hard` is not.

### Several Git features are unsupported, and the list intersects this method

Unsupported outright:

- **`.gitattributes`** - so merge drivers, generated-file marking and
  end-of-line handling do not apply.
- **Hooks** - so any check wired as a pre-commit or pre-push hook does not run.
- **`git-worktree`** - Jujutsu has its own workspaces instead.
- **Submodules**, **partial clones**, **Git LFS**, **sparse checkouts**.

Partially supported:

- **Configuration** - only remotes and `core.excludesFile` are respected. So a
  repository's git configuration is largely inert under Jujutsu.
- **Tags** - lightweight tags can be created and checked out; annotated tags
  cannot.
- **The staging area** - ignored, and _"`jj diff` will show a diff from the Git
  HEAD to the working copy"_.
- **Shallow clones** - deepening is unsupported.

Three of these matter to this project specifically. Hooks being unsupported
means a repository relying on them for a check has no check under Jujutsu, and
that must be reported rather than assumed equivalent. `.gitattributes` being
unsupported means a repository that marks generated files loses that marking.
And annotated tags being unsupported matters to any release process that signs
a tag, since a signed tag is an annotated tag.

### Signing is configurable, verification is off by default

`signing.backend` selects gpg, gpgsm, ssh or none; `signing.key` names the key;
`signing.behavior` decides when signing happens, with four values:

| Value   | What it does                                                        |
| ------- | ------------------------------------------------------------------- |
| `drop`  | Do not sign; drop an existing signature when the change is modified |
| `keep`  | Sign again only if it was signed before and you authored it         |
| `own`   | Sign every commit you authored when you modify it                   |
| `force` | Sign after modification unconditionally                             |

`drop` is the one to notice. Under it, modifying a signed commit silently
removes the signature. Jujutsu modifies commits constantly, because that is its
working model, so a repository requiring signed commits and configured with
`drop` loses signatures during ordinary work.

Verification is _disabled by default for performance_, and is enabled with
`ui.show-cryptographic-signatures = true`. Once on, a signature is reached
through `commit.signature()` in a template.

So a harness verifying signatures over a Jujutsu repository either enables that
setting or verifies through git, and the second is simpler and uses the `%G?`
vocabulary already established.

`git.sign-on-push = true` is the alternative model: sign when pushing rather
than when committing, which suits Jujutsu's habit of rewriting commits.

### Machine-readable output comes from templates, including a JSON function

There is no `--json` flag. Output is shaped by a functional template language
with `-T`, and the documentation gives `jj log -G -T 'commit_id ++ " " ++
change_id ++ "\n"'` as the machine-readable pattern. A `json(value)` function
serialises a value, and `.escape_json()` on a string is described as useful for
machine-readable templates.

That is more capable than a fixed JSON output and more work: the pack owns the
template, and the template is the contract. A template written once and stored
with the pack is the right shape, rather than a format string assembled at each
call site.

### Workspaces replace worktrees, and staleness is explicit

Several workspaces may share one repository, each with a different commit
checked out. When one workspace modifies a commit another has checked out, the
second becomes **stale**, and `jj workspace update-stale` brings it up to date.

That is a better story than git's for parallel work, because the conflicting
state is named and has a command rather than being an inconsistency a user
discovers. It is also a different one, so a pack cannot treat `jj workspace` as
`git worktree` with a different spelling.

### What the pack authors

Jujutsu configuration for signing behaviour and templates. It does not author
`.gitattributes` or hooks for a Jujutsu-only repository, because neither has
any effect.

### What a reviewer needs that no command reports

Whether the repository is colocated, because the answer changes which tool may
safely be run.

Whether `signing.behavior` is `drop` in a repository that requires signatures.

Whether a check the project believes runs as a hook actually runs.

Whether the change identifier or the commit identifier is the stable one for a
given purpose - Jujutsu's change identifier survives a rewrite and the commit
identifier does not, which inverts the git habit.

### What the skill has to contain

In the body, in this order:

1. Reading is writing. Every `jj` command snapshots the working copy, so
   inspection uses git's read-only commands in a colocated workspace.
2. Detection. Colocated or not, and which of the two tools may write.
3. The unsupported list, with the three that matter to this method: hooks,
   `.gitattributes`, annotated tags.
4. Signing. The four behaviours, that `drop` loses signatures under normal
   use, and that verification is off by default.
5. Machine-readable output through a stored template with `json()`.
6. What must never happen. Running a `jj` command to inspect. Assuming a
   hook runs. Creating a signed tag through Jujutsu. Treating `jj workspace` as
   `git worktree`.

In supporting files: the unsupported and partially supported lists; the
signing behaviour table; the stored templates; the workspace and staleness
commands; and the dated facts with what to re-check.

## Conclusions

1. A colocated workspace is the supported shape, and is the default for
   `jj git init` and `jj git clone`.
2. Inspection uses git's read-only commands, because every `jj` command
   snapshots and commits the working copy and there is no read-only
   invocation.
3. A `jj` command run by the harness is recorded in the operation log,
   which makes it undoable, and that recoverability is stated rather than
   relied on silently.
4. Import and export happen on every command, so git and Jujutsu agree
   without an explicit synchronisation step.
5. Hooks do not run under Jujutsu, so a repository relying on a hook for a
   check has no check, and the pack reports that rather than assuming
   equivalence.
6. `.gitattributes` has no effect, so generated-file marking, merge drivers
   and end-of-line handling are absent.
7. Annotated tags cannot be created, which means a signed tag cannot be, so
   a release process that signs tags does not run through Jujutsu.
8. Only remotes and `core.excludesFile` are read from git configuration, so
   the rest of a repository's git configuration is inert.
9. `signing.behavior = drop` loses signatures during normal work, because
   Jujutsu modifies commits constantly, and a repository requiring signatures is
   reported when it is configured that way.
10. Signature verification is off by default and is either enabled
    explicitly or performed through git, and the second reuses the `%G?`
    vocabulary already established.
11. Machine-readable output is a stored template using `json()`, owned by
    the pack, rather than a format string assembled per call.
12. `jj workspace` is not `git worktree`. Workspaces have an explicit stale
    state with a command to resolve it, which git has no equivalent of.
13. The change identifier and the commit identifier answer different
    questions, since the change identifier survives a rewrite, which inverts
    the git habit of citing a commit.
14. The skill body carries that reading is writing, detection, the
    unsupported list, signing, machine-readable output, and the
    prohibitions, in that order.

## Sources

All read 2026-09-20.

- [Git compatibility](https://docs.jj-vcs.dev/latest/git-compatibility/) -
  colocated workspaces as the default for `jj git init` and `jj git clone`;
  automatic import and export on every `jj` command with the recommendation to
  keep Git commands read-only; the unsupported list of `.gitattributes`, hooks,
  submodules, partial clones, Git LFS, `git-worktree` and sparse checkouts; and
  the partially supported list of configuration limited to remotes and
  `core.excludesFile`, lightweight but not annotated tags, an ignored staging
  area with `jj diff` showing Git HEAD against the working copy, shallow clones
  without deepening, and garbage collection described as safe but untested.
- [Working copy](https://docs.jj-vcs.dev/latest/working-copy/) - the absence of
  a staging area; that most `jj` commands commit working-copy changes when they
  have changed; implicit tracking of new and deleted files; the three steps of
  snapshot, in-memory commit creation and working-copy update, each recorded as
  an operation; multiple workspaces with different commits checked out; and the
  stale state resolved by `jj workspace update-stale`.
- [Configuration](https://docs.jj-vcs.dev/latest/config/) - `signing.backend`
  with gpg, gpgsm, ssh or none; `signing.key`; the four `signing.behavior`
  values `drop`, `keep`, `own` and `force` with their definitions; verification
  disabled by default for performance and enabled with
  `ui.show-cryptographic-signatures`; `commit.signature()` and the short and
  detailed formatting functions; and `git.sign-on-push`.
- [Templates](https://docs.jj-vcs.dev/latest/templates/) - the functional
  template language for customising output; the machine-readable pattern with
  `-T`; the `json()` serialisation function; and `.escape_json()` described as
  useful for machine-readable templates.
