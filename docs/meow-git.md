# meow-git

`meow-git` is a pack for repositories that use `git`. It refuses a commit on
the trunk you declare, and before a push runs it checks every commit the push
would publish: the message against your commit convention, and the signature
where you require one. It installs on its own, and it uses `meow-scm` for the
message check where that unit is installed.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-git@meowpaw
```

## Declare your policy

Put it under `[git]` in `.meowpaw/profile.toml`:

```toml
[git]
trunk = "main"
require_signatures = true
```

## What it does

When Claude Code runs `git commit` on the trunk, the pack refuses it and says
to take a branch. On any other branch the commit runs.

When Claude Code runs `git push`, the pack reads every commit reachable from
the current head that no remote-tracking branch already has, and refuses the
push if any of them fails, naming each failing commit:

```text
meow-git: refused the push; 1 problem in the 2 commits it would publish:

3f2a91c fix: stop the retry loop
    signature: the commit is unsigned
```

A message is checked with `meow-scm check-message` against the convention you
declared under `[commits]`. Where `meow-scm` isn't installed, the pack says
the message check is unrun, and never that it passed.

Where you require signatures, only a good signature from a key your repository
trusts passes. A commit that is signed but can't be verified here, because the
key or the list of allowed signers is missing, is reported as unverifiable, and
never as unsigned. A commit that fails can still be amended, because nothing
has left the machine.

Without a `[git]` table, the pack refuses nothing on commit, still checks
messages on push, and says the trunk and the signing policy are undeclared.

## What it costs you

Nothing in context: the pack is two hooks, and each runs only on its own
command. A push takes one message check and one signature check per commit.
The program is a native binary shipped inside the pack, so it needs nothing
installed on the machine; on a machine the pack carries no binary for, it says
it checked nothing and blocks nothing.

## Where the rules come from

The decision is
`project/adrs/ADR-1090-a-git-pack-enforces-the-convention-at-push.md`, and the
pack is specified in `project/specs/SPC-1060-the-git-pack.md`.
