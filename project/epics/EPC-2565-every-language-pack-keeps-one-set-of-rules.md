---
id: EPC-2565
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2670
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Every language pack runs what the repository configured, and reports what it left unchecked

Realises exactly one authorising record, ADR-2670. The epic is complete when
a shared layer in `crates/meow/`, which every language pack uses, holds the
rules SPC-1190 states under "What a pack runs", "What a pack reports it
didn't check", "What a pack never changes" and "What a pack keeps", each held
by a fixture pack in the crate's tests, and `meow-markdown` runs on that layer
wherever a rule applies to Markdown.

## Acceptance criteria

Taken from ADR-2670's list of how it will be known realised, criterion 1 of
which SPC-1190 already meets by stating each rule with its requirement:

1. A fixture pack bound to a tool the repository configured, beside one it
   didn't, binds the configured one, and the shared layer refuses a binding
   that turns on a lint group the repository didn't ask for (REQ-2420,
   REQ-2422).
2. A fixture pack whose clean report omits its rule groups or severity level
   fails the shared layer's test (REQ-2432, REQ-2444).
3. A fixture verb that writes a file into the working tree fails the shared
   layer's test (REQ-2442).
4. A fixture verb whose ecosystem has a machine-readable format records its
   result in it, and one with none says the evidence is captured output
   (REQ-2416).
5. Every requirement ADR-2670 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-5120 hold what a pack runs in the shared pack layer of `crates/meow/`
      closes: REQ-2420, REQ-2422, REQ-2426, REQ-2428, REQ-2446, REQ-2448

- [ ] T-002 [P] TSK-5125 hold what a pack reports it didn't check in the shared pack layer
      closes: REQ-2410, REQ-2412, REQ-2414, REQ-2432, REQ-2436, REQ-2444
      depends: TSK-5120 (not blocking) - both add rules to the same shared layer, and either can land first

- [ ] T-003 [P] TSK-5130 hold what a pack never changes in the shared pack layer
      closes: REQ-2430, REQ-2440, REQ-2442
      depends: TSK-5120 (not blocking) - both add rules to the same shared layer, and either can land first

- [ ] T-004 [P] TSK-5135 hold what a pack keeps in the shared pack layer
      closes: REQ-2416, REQ-2418, REQ-2450
      depends: TSK-5120 (not blocking) - both add rules to the same shared layer, and either can land first

## Coverage

Each of the eighteen requirements ADR-2670 addresses lands in exactly one
task. The four tasks run in parallel, and each adds its rules to the same
shared layer, so the second to land rebuilds on the first. TSK-5120 and
TSK-5130 are the smallest set that tests the decision, because a pack that
runs only what the repository configured and changes nothing it wasn't asked
to is the claim the rest reports on.

## Not covered

ADR-2670's second criterion, the Rust pack's fixtures for documentation
tests, a pinned toolchain and output kept outside the tree, because the Rust
pack is EPC-2560's TSK-5075, which depends on this epic's four tasks and
carries those fixtures. Which tool each pack binds, which ADR-2670 leaves to
each pack's own document.
