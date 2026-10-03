---
id: TSK-4420
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2340
closes:
  [
    REQ-1480,
    REQ-1481,
    REQ-1483,
    REQ-1484,
    REQ-1488,
    REQ-1494,
    REQ-2994,
    REQ-3000,
  ]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold the rest of the plugin contract with tests

Tests hold the parts of SPC-1080's "Each unit is a plugin" that already hold in
the tree: every unit installs from the marketplace with no installer, reaches
another only through files and commands, writes nothing under its install
root, keeps machine-specific settings out of its files, stays at major
version zero, and keeps its configuration in TOML. One task, one branch, one
pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given `.claude-plugin/marketplace.json`, when a test reads it, then every
   directory under `plugins/` has an entry, and no unit ships a file named as
   an install script or a `postinstall` step (REQ-1480). Closed by: a test in
   `tools/test_marketplace.py` naming REQ-1480.
2. Given every unit's `plugin.json`, when a test reads it, then each version's
   major number is 0 (REQ-2994). Closed by: a test naming REQ-2994.
3. Given each unit's fixtures run against a read-only copy of the unit's
   directory, when they run, then none fails on a write under that directory
   (REQ-3000, REQ-1484). Closed by: a test naming both, seen failing first
   where any unit writes there.
4. Given every file of configuration a unit ships or reads, when a test lists
   them, then each is TOML, apart from the platform's own JSON manifests and
   hooks and the record's YAML front matter (REQ-1494). Closed by: a test
   naming REQ-1494.
5. Given every unit's shipped files, when a test reads them, then none holds
   an absolute path to a home directory or a credential's value (REQ-1488).
   Closed by: a test naming REQ-1488.
6. Given `tools/check_standalone.py` and the hooks every unit ships, when a
   reviewer reads them, then no unit reads another's files except through a
   command, and no hook's answer assumes another unit's hook ran first
   (REQ-1481, REQ-1483). Closed by: `tools/check_standalone.py` in the
   `lint` verb for REQ-1481, and judgement in the review for REQ-1483.

## What to do

Add the tests beside the ones in `tools/` that already read the repository,
and list each new file in the profile's `test` verb. Where a test finds a unit
breaking the rule, fix the unit in the same pull request, because the test is
the first check of a rule the tree was assumed to meet.

## Depends on

- TSK-4390 (not blocking): both read every unit's manifest, and either can land first.

## Evidence

Not yet.

Criterion 6 rests on judgement for REQ-1483, because no program reads which
hook a rule relies on running first.

## Left alone

When the harness leaves major version zero, which no decision settles yet;
the test in criterion 2 changes in the pull request of the decision that
does.
