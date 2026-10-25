---
id: BUG-1690
artifact: bug
status: approved
severity: minor
enters: requirements
found: 2026-10-25
revised: 2026-10-25
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The wrapper names the wrong fix for a marketplace added from the GitHub repository

Every launcher's "no `paw` executable was found" message tells the person to
run `claude plugin install meow-core@meowpaw`. Where the marketplace was added
with source `github` against `meowshed/meowpaw`, that install already
succeeded and the message returns unchanged, because that source installs
each unit as its git subdirectory, and `plugins/meow-core/bin/` carries no
binary there: the binaries are gitignored in the tree and ship only inside
the release archive (ADR-2810).

## Reproduction

macOS, Darwin, arm64, a session with no `meow-core` installed yet:

1. Run `claude plugin marketplace add --source github meowshed/meowpaw`, then
   `claude plugin install meow-core@meowpaw`. The install reports success.
2. Run any Bash command the `meow-git`, `meow-github` or `meow-loop` hooks
   guard. The guard calls a launcher such as `plugins/meow-git/bin/meow-git`
   (or the installed unit's own copy), which reports: "no paw executable was
   found for this machine, Darwin on arm64; install meow-core, which ships the
   shared binary for macOS, Linux and Windows on arm64 and x86_64", and denies
   the call.
3. Run `claude plugin install meow-core@meowpaw` again, as told. It reports
   the unit already installed, or reinstalls the same source. Run the guarded
   command again: the same message returns.
4. Confirm the cause: `~/.claude/plugins/cache/meowpaw/meow-core/<version>/`
   holds `.claude-plugin`, `hooks`, `output-styles`, `tests`, `README.md`,
   `CHANGELOG.md` and `requires.toml`, and no `bin/`.

## What the system does

The launcher template (`tools/launchers.toml`, rendered by
`tools/generate_launchers.py` into every unit's `bin/<name>` and
`plugins/meow-flow/bin/paw`) prints one fixed sentence for every machine that
can't resolve a binary, naming the one remedy that fixes a stale or missing
install from the archive-backed marketplace. It never checks which source
installed the unit, so the same sentence reaches a person for whom that
remedy is a no-op, with nothing to try next.

## What it should do, and why

No requirement in force states what the message must say when a `paw`
resolution fails, which is the gap this defect names. The message should
name, for a marketplace known to carry no binary, that cause, and the address
of the marketplace that does (`meow.retran.me`), because a person who follows
the message's own advice and sees it return unchanged has no way to find that
cause from the message alone.

## Triage

Enters at requirements, because no requirement in force states the
obligation the fix would hold, so the requirement is written first and the
fix follows it. Minor, because the archive-backed marketplace the README
names still works end to end; this defect strands only a person who chose
the `github` source, with a message that sends them in a circle rather than
blocking them outright.

## Closed by

Not yet closed.

## Tasks

- [ ] T-001 TSK-5700 name the cause and the working marketplace address in
      the launcher template's unresolved-binary message, in
      `tools/launchers.toml`, regenerated into every unit's launcher
