---
id: BUG-1150
artifact: bug
status: approved
severity: major
found: 2026-09-26
revised: 2026-09-26
issue: 195
---

# The crate's tests could share a temporary directory, so the gate failed at random

## Reproduction

On macOS 27.0 with Rust 1.98.1, at the revision #194 left, build the crate's
tests and run the `profile` tests 300 times:

```bash
cargo test --manifest-path crates/meow/Cargo.toml --all-features --no-run
for i in $(seq 300); do target/debug/deps/meow-<hash> profile -q || echo failed; done
```

Three of the 300 runs failed. In a full `mise run all`, the failure showed as
the gate exiting 101 with no failing task in view, four times across a day.
The fifth time the log named the test:

```text
profile::tests::a_broken_profile_is_unparseable_and_says_why --- FAILED
panicked at src/profile.rs:77:18: expected unparseable
```

## What the system does

The test helper named each temporary directory from the process id and the
clock in nanoseconds. The tests run in parallel threads of one process, so two
of them could read the same clock value and share one directory. One test then
read the profile another had written, or lost its directory when the other
dropped it.

## What it should do, and why

Each test gets a directory of its own, so the gate fails only when the code
does. No requirement states this directly. A gate that fails at random teaches
the person reading it to rerun rather than read, and the principle in
`CLAUDE.md` says such a check gets switched off.

## Triage

Implementation, in the crate's test helper. The severity is major because the
gate is what every pull request stands on, and twice the failure let a commit
through a script that chained the gate with `;`.

## Closed by

The helper adds a process-wide counter to each directory's name. After the
fix, the same loop ran the `profile` tests 1,300 times with no failure, where
the rate before predicts about 13.
