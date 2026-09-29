---
id: BUG-1267
artifact: bug
status: approved
severity: minor
violates: REQ-1756
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue: 719
---

# No fixture pins the prose gate's P1 to whole words

P1 in `crates/meow/src/prose.rs` matches an idiom as whole words, as ADR-1600
decides, but no fixture holds an idiom's words inside longer words. So a P1
that matched a plain substring would block `circle backend` and `deep diver`,
and every check would still pass. The four texts from BUG-1230 hold no
fragment of an idiom, so they don't guard this, and only the masking of code,
URLs and paths is pinned.

## Reproduction

`main` after #717, with `meow-prose-gate` 0.2.0, on macOS on arm64.

1. In `rule_p1` in `crates/meow/src/prose.rs`, remove the two `\b` from the
   pattern, so an idiom matches anywhere in a word.
2. Run `crates/meow/build-units`, then `python3 -m unittest test_gate` in
   `plugins/meow-prose-gate/tests` and
   `cargo test --manifest-path crates/meow/Cargo.toml --features prose`.

## What the system does

Every fixture and every Rust test passes against the changed P1. The current
binary lets `git commit -m "Route the circle backend through the cache"` and
`git commit -m "a deep diver"` through with exit 0, and no check observes that
it does.

## What it should do, and why

A fixture should hold idiom words inside longer words and expect the text to
pass, so a P1 that matches a fragment fails a check. REQ-1756 asks a check to
match the defect and never a word that can appear innocently, and P1's whole
word match is how the gate meets it.

## Triage

It enters at cover, because REQ-1756 is right and the program meets it: the
checks miss what it asks. Minor, because P1 matches whole words today, and
only the guard against a regression is missing.

## Closed by

A fixture in the class `ReadableTexts` in
`plugins/meow-prose-gate/tests/test_gate.py` and a Rust test in
`crates/meow/src/prose.rs`, each holding `circle backend`, `deep diver` and
`undercircle back` and expecting no finding, and each seen failing against P1
with its word boundaries removed.

## Tasks

- [ ] T-001 TSK-2577 pin P1 to whole words, in
      `plugins/meow-prose-gate/tests/test_gate.py` and
      `crates/meow/src/prose.rs`
