---
id: TSK-1350
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1080
closes: [REQ-0032, REQ-0076]
issue: 150 151 152 153
---

# Build the crate, and run the verbs on it

One task, one branch, one pull request, one review.

## What to do

Create `crates/meow/` as SPC-1080 states: one binary, a feature per unit, and a
shared module for the profile, the report shapes and the exit codes (REQ-0076).
Port `meow-verbs`' program to the `verbs` subcommand, change its launcher to
pick `bin/<target>/meow` and report every verb unrun where there is none, and
delete `lib/meow_verbs.py`. Add `mise run build` for the local build, ignore the
binaries, and run the crate's tests in the gate.

Keep the tool's record and tracker features out of every step the units run,
so each unit is complete without them (REQ-0032).

## Depends on

Nothing. ADR-1110 and SPC-1080 are approved. Building on this machine needs
the Xcode licence accepted.

## Evidence

`crates/meow/` builds one binary with a feature per unit: `verbs`, and the
empty `scm`, `git` and `record` the ports fill (REQ-0076). The shared module
reads the repository's root and its profile as absent, unparseable or parsed.
`meow verbs` is `meow-verbs`' program, ported line for line; the launcher names
the machine's target, runs `bin/<target>/meow`, and reports every verb unrun
where there is none. `lib/meow_verbs.py` is deleted. `crates/meow/build-units`,
run by `mise run build` and by this repository's `test` verb, builds each unit's
binary into its ignored `bin/<target>/`. The gate runs the crate's tests. No
record or tracker feature exists in the crate yet, so no unit depends on one
(REQ-0032).

```text
$ git diff --stat origin/main -- plugins/meow-verbs/tests
(nothing: the fixtures are unchanged)

$ python3 -m unittest discover -s plugins/meow-verbs/tests
Ran 12 tests in 0.530s
OK

$ cargo test --manifest-path crates/meow/Cargo.toml --all-features
test result: ok. 3 passed; 0 failed

$ MEOW_VERBS_BIN=stub/meow-verbs python3 -m unittest discover -s plugins/meow-verbs/tests
FAILED (failures=6, errors=6)
```

The `verbs` binary for `aarch64-apple-darwin` is 504,336 bytes.

Two things surfaced. The first local build copied a new binary over the old
one, and macOS killed it on its next run, because it caches a binary's code
signature per file; `build-units` now replaces the file. And the kind SPC-1040
calls "no interpreter" now means the unit carries no binary for the machine;
it keeps its name so that the fixtures defining it didn't change in the port,
and SPC-1040 says so. REQ-0032 and REQ-0076 are closed.

## Left alone

The other units' programs, and the release.
