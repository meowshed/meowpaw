---
id: TSK-5700
artifact: task
status: approved
revised: 2026-10-25
realises: ADR-3070
closes: [REQ-5200]
issue:
produces:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Name the cause and the working marketplace address in the unresolved-binary message

Every launcher's unresolved-binary message probes, before it names
`claude plugin install meow-core@meowpaw`, whether its own directory sits
under a `github`-source install with no binary, and where it does, names
that cause and `meow.retran.me` instead.

## Acceptance criteria

1. Given a launcher with no `<cpu>-<system>/` directory at all under its own
   `bin/`, when it runs with no cached or resolvable binary, then it denies
   naming the cause (a `github`-source marketplace ships no binary here) and
   `meow.retran.me`. Closed by: `tools/test_generate_launchers.py`'s new case.
2. Given a launcher whose `bin/` holds at least one `<other-target>/`
   directory but none for this machine, when it runs with no resolvable
   binary, then it denies naming `claude plugin install meow-core@meowpaw`
   exactly as it does on the trunk today. Closed by: the existing no-binary
   fixtures in `tools/test_generate_launchers.py` and
   `tools/test_launchers.py`, unchanged.

## What to do

Add the probe and the two message branches to the unresolved-binary section
of `tools/launchers.toml`, the template `tools/generate_launchers.py` renders
into every unit's `bin/<name>` launcher and `plugins/meow-flow/bin/paw`.
Regenerate every launcher with `python3 tools/generate_launchers.py` and
commit the regenerated copies alongside the template, since
`tools/generate_launchers.py --check` (part of `test-record`) fails a launcher
the template and the checked-in copy disagree on. Extend
`tools/test_generate_launchers.py` with the `github`-source fixture ADR-3070
names. Update SPC-1240's `### A hook whose program is missing` section if the
rendered wording changes from what ADR-3070 already put there.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The archive-backed marketplace's own message, and every other launcher
behaviour ADR-2710 decided, which this task leaves exactly as it runs today.
