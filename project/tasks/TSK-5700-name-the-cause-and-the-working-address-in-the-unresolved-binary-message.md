---
id: TSK-5700
artifact: task
status: done
revised: 2026-10-25
realises: ADR-3080
closes: [REQ-5200]
issue:
produces:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Name the cause and the working marketplace address in the unresolved-binary message

Every launcher's unresolved-binary message probes, before it names
`claude plugin install meow-core@meowpaw`, the `meow-core` install it would
otherwise resolve the shared binary from, and where that install carries no
binary for any machine, names that cause and `meow.retran.me` instead.

## Acceptance criteria

1. Given a launcher whose resolved `meow-core` install (via its `meow-root`
   pointer) carries no `<cpu>-<system>/` directory at all under its `bin/`,
   when the launcher runs with no cached or resolvable binary, then it
   denies naming the cause (a `github`-source marketplace ships no binary
   here) and `meow.retran.me`. Closed by:
   `tools/test_generate_launchers.py`'s new `Denial` case.
2. Given a launcher whose resolved `meow-core` install's `bin/` holds at
   least one `<other-target>/` directory but none for this machine, or
   whose `meow-root` pointer resolves to no install at all, when it runs
   with no resolvable binary, then it denies naming `claude plugin install
meow-core@meowpaw` exactly as it does on the trunk today. Closed by: the
   other two `Denial` cases in the same file.

## What to do

Add the probe and the two message branches to the unresolved-binary section
of `tools/launchers.toml`, the template `tools/generate_launchers.py` renders
into every unit's `bin/<name>` launcher and `plugins/meow-flow/bin/paw`,
reading `$root` once `CLAUDE_FIND` has resolved it rather than the caller's
own `bin/`. Introduce a `fix` variable alongside `reason`, since the install
command every guarded launcher (`meow-git`, `meow-github`, `meow-loop`,
`meow-prose-gate`, `meow-flow`'s `SessionStart` print, `meow-checks
revision`) appends after `$reason` must vary with the branch too. Regenerate
every launcher with `python3 tools/generate_launchers.py` and commit the
regenerated copies alongside the template, since `tools/generate_launchers.py
--check` (part of `test-record`) fails a launcher the template and the
checked-in copy disagree on. SPC-1240's `### A hook whose program is
missing` section already states the probe ADR-3080 decided; update it only
if the implementation's rendered wording differs from what is there.

## Depends on

Nothing.

## Evidence

`python3 -m unittest tools.test_generate_launchers.Denial -v`: 3 passed,
proving both criteria — the no-target-at-all case names the cause and
`meow.retran.me`, the other-target and no-install cases name `claude plugin
install meow-core@meowpaw` unchanged. `python3 tools/generate_launchers.py
--check`: 61 generated files equal their template. `mise run all`: every
stage passed, including `test-tools` (244 tests, 0 findings across every
record and documentation check) and `shell-lint` (clean after introducing a
`fix` variable only into the launchers that read it, so `shellcheck`'s
unused-variable rule holds on every file). Pull request 1133 (BUG-1690's
closing task).

## Left alone

The archive-backed marketplace's own message, and every other launcher
behaviour ADR-2710 decided, which this task leaves exactly as it runs today.
