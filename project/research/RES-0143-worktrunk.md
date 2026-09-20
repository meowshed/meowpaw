---
id: RES-0143
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0131, RES-0005
---

# worktrunk

## Summary

This tool was built for the situation the harness creates: several agents in
parallel, each needing a working directory the others cannot disturb. Its
defaults were chosen for that case. Its merge command is the one to read
carefully: it composes four decisions this method reserves, including a
generated commit message and a rebase after signing. It documents no
machine-readable output, so state is read from git and the tool is used for
operations.

Research for one supported tool. worktrunk manages git worktrees, and it was
built for the situation this harness creates: several agents working in
parallel, each needing a working directory the others cannot disturb.

It covers what it adds over `git worktree`, what its merge command actually
does, where its automation hooks fire, what it shares between worktrees, what
the pack authors, and what the skill has to contain.

It does not cover git's own worktree mechanics, which are
[RES-0131-git.md](RES-0131-git.md).

## The question

git already has worktrees. The question is what a wrapper adds that pays for a
dependency, and which of its conveniences a harness may use without losing
control of what happened.

## Method

We fetched and read the project's repository on 2026-09-20 for the command set,
the hook points, and the build-cache mechanism with its filesystem conditions.
We also read the merge command's full sequence, which is what the conclusions
turn on.

The absence of a documented machine-readable output was checked by reading the
repository rather than assumed, and is stated as an absence.

The project's own framing and its install routes came from its site and one
secondary account, and are marked as such. Nothing was installed or run.

## Findings

### It is built for the case this harness has

worktrunk is a command-line tool for git worktree management, _designed for
parallel agent workflows_. Its premise is that agents handling longer tasks
unsupervised, five to ten at a time, each need their own working directory, so
none disturbs another's changes.

That matches delegation directly, and it means the tool's defaults
were chosen for this situation rather than adapted to it.

Installation is through Homebrew, Cargo, Winget or the Arch user repository, so
it is not a dependency a pack can assume is present.

### Three commands, and one of them does considerably more than its name

`wt switch <branch>` creates a worktree and switches to it, with `-c` to create
the branch and `-x` to run a command afterwards.

`wt list` shows the worktrees with status: branch name, staged changes, commits
ahead of and behind the main branch, remote status, commit hash, age and
message. A `--full` mode adds continuous-integration status and
model-generated summaries.

`wt remove` deletes the current worktree and its branch.

`wt merge <target>` repays careful reading, because it is a whole workflow in
one verb. It generates a commit message, commits the staged changes, rebases
onto the target branch, performs a fast-forward merge, and then removes the
worktree and the branch in the background.

Every step of that is something this method has rules about. The commit message
is generated rather than written, and this method requires a commit message to
say why. The commit is made from whatever was staged, which is a decision about
scope taken by the tool. The rebase rewrites commits, which changes what was
signed. And the removal happens in the background, so the worktree the harness
was working in may be gone before the harness notices.

So `wt merge` is not a command a harness invokes as a convenience. It composes
four decisions the method reserves for itself, and a pack that calls it has
delegated all four. The individual operations remain available and are what a
pack uses.

The same reasoning applies to `--full`'s model-generated summaries: they are a
model's description of a diff, which is a useful thing for a person glancing at
a list and is not evidence about anything.

### Hooks are the part that is genuinely useful to a harness

Automation fires at three lifecycle points: **create**, when a worktree is
made; **pre-merge**; and **post-merge**. Configuration uses templates with
branch-scoped variables.

The create hook is the valuable one. A fresh worktree is an empty directory
with a checkout - no dependencies installed, no environment prepared, no
generated files - and every agent given one has to do that work before it can
start. A create hook does it once, declaratively, and a pack that configures it
removes a class of _the agent could not build_ failures that are not about the
code.

### Build cache sharing is a filesystem feature, and it has conditions

worktrunk can share `target/`, `node_modules/` and similar build outputs across
worktrees _"without building or copying them"_ on APFS, btrfs and XFS, through
`wt step copy-ignored`.

The mechanism is copy-on-write cloning, which is why the filesystem list is
short. On a filesystem not in that list the feature is unavailable, and a pack
that relies on it produces a setup that works on one machine and is slow on
another.

What is shared is ignored build output, and never source. The isolation between
worktrees is preserved for everything that is tracked, which is what makes this
safe rather than clever.

### No machine-readable output is documented

The listing is rich and human-shaped, and nothing in the documentation
describes a JSON form.

So a pack that needs worktree state as data reads it from `git worktree list
--porcelain`, which is documented and stable, and uses worktrunk for the
operations rather than for the answers. The document states that division
plainly, because the temptation is to parse the nicer output.

### What the pack authors

The worktrunk configuration: the path template and the create hook, which is
where a project says how a fresh worktree becomes a working one.

It does not author pre-merge or post-merge hooks that perform the merge
decisions, for the reason above.

### What a reviewer needs that no command reports

Whether a commit message on the branch was generated or written, since only one
of those says why.

Whether the branch was rebased after it was signed.

Whether a worktree was removed while something was still using it.

Whether the create hook is doing something the project's own setup should be
doing, which is a question about where the knowledge lives.

### What the skill has to contain

In the body, in this order:

1. What worktrunk is for. Operations on worktrees, not answers about them.
2. State comes from git. `git worktree list --porcelain` is the data
   source; worktrunk's listing is for people.
3. The merge rule. `wt merge` composes four decisions the method reserves,
   so the pack uses the individual operations instead.
4. The create hook, as the mechanism that makes a fresh worktree usable and
   the place to configure it.
5. What must never happen. Calling `wt merge`. Parsing the human listing.
   Citing a generated summary as evidence. Assuming cache sharing works on any
   filesystem.

In supporting files: the command reference; the hook points and template
variables; the filesystem conditions for cache sharing; and the dated facts
with what to re-check.

## Conclusions

1. worktrunk is used for operations and not for answers. Worktree state is
   read from `git worktree list --porcelain`, which is documented and stable,
   because worktrunk documents no machine-readable output.
2. `wt merge` is not called by the harness, because it generates a commit
   message, commits whatever is staged, rebases, fast-forward merges and
   removes the worktree in the background - four decisions this method reserves
   for itself.
3. A generated commit message is not accepted, since a commit message here
   has to say why and a generated one describes what.
4. A rebase after signing is treated as a change to what was signed, so a
   workflow that rebases automatically is not used where signatures are
   required.
5. Background removal is avoided, because a worktree that disappears while
   something is using it fails in a way that is hard to attribute.
6. A model-generated summary is not evidence, and is used only where a
   person is reading a list.
7. The create hook is configured, because a fresh worktree is an empty
   checkout and preparing it once declaratively removes failures that are not
   about the code.
8. Build cache sharing is used where the filesystem supports it and reported
   where it does not, since it depends on copy-on-write cloning available
   only on APFS, btrfs and XFS.
9. Only ignored build output is shared, never tracked source, which is what
   keeps the worktrees isolated.
10. worktrunk is not assumed present, since it installs through a package
    manager rather than shipping with anything.
11. The skill body carries what the tool is for, where state comes from, the
    merge rule, the create hook, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [max-sixty/worktrunk](https://github.com/max-sixty/worktrunk) - a
  command-line tool for git worktree management designed for parallel agent
  workflows; `wt switch` with `-c` and `-x`; `wt list` showing branch, staged
  changes, commits ahead and behind, remote status, hash, age and message, with
  a `--full` mode adding continuous-integration status and model-generated
  summaries; `wt merge` generating a commit message, committing staged changes,
  rebasing onto the target, fast-forward merging and removing the worktree and
  branch in the background; `wt remove`; hooks at create, pre-merge and
  post-merge with branch-scoped template variables; a configurable path
  template; and build cache sharing of `target/`, `node_modules/` and similar
  across worktrees without building or copying on APFS, btrfs and XFS through
  `wt step copy-ignored`. No JSON output is documented.
- [worktrunk.dev](https://worktrunk.dev/) and
  [the project's own description](https://daily.dev/posts/worktrunk-git-worktree-manager-for-ai-agent-workflows-edzkcvip6)
  - the premise of five to ten agents in parallel each needing an isolated
    working directory, and installation through Homebrew, Cargo, Winget or the
    Arch user repository. Recorded as the project's own framing and a secondary
    source.
