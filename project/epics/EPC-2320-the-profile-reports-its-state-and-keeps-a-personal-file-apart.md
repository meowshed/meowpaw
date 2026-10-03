---
id: EPC-2320
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2370
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The profile reports its state and unknown keys, and keeps a personal file apart

Realises exactly one authorising record, ADR-2370. The epic is complete when
every command that reads the profile prints its state, names each key the
table of keys doesn't list, reads a personal profile that only `[verbs]` fills,
refuses a machine path in it, and checks a commit type against the profile's
own list, as SPC-1080, SPC-1040 and SPC-1050 state.

## Acceptance criteria

Taken from ADR-2370's list of how it will be known realised:

1. A fixture with a profile in the parent of the repository root and none in
   the root reports `absent` (REQ-2940).
2. A fixture whose profile has a syntax error reports `unparseable` with the
   parser's message, resolves all five verbs as unresolved and runs no
   fallback (REQ-2948).
3. A fixture with the key `tset` under `[verbs]` reports `tset` once, runs the
   other verbs, and exits as it would without the key (REQ-2942).
4. Every key in the table has a reason in the source, and a test fails for an
   entry without one (REQ-2950).
5. Creating `.meowpaw/profile.local.toml` through the tool adds it to
   `.git/info/exclude` and changes no tracked file (REQ-2944).
6. A personal `test = "/Users/someone/bin/runner"` leaves `test` unresolved and
   the report names a machine path as the cause. The same value in a shared
   profile is not refused by this rule (REQ-2946).
7. A repository whose profile lists its own commit types rejects a commit whose
   type is outside that list, even when the type is a conventional one
   (REQ-2952).
8. Every requirement ADR-2370 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [x] T-001 TSK-4300 print the profile's state and name each unknown key, from one table of keys, in `crates/meow/src/profile.rs`
      closes: REQ-2940, REQ-2942, REQ-2948, REQ-2950
      evidence: `crates/meow/tests/profile_states.rs` and the table's tests pass in local runs of `mise run all` and `meow-checks run test`, #818

- [ ] T-002 TSK-4310 read a personal profile, write it with `meow-checks local`, and refuse a machine path in it
      closes: REQ-2944, REQ-2946
      depends: TSK-4300 (blocking) - a table other than `[verbs]` in the personal file is reported through the unknown-key list TSK-4300 adds

- [ ] T-003 [P] TSK-4320 check a commit type against the profile's `[commits.types]` alone, in `meow-scm`
      closes: REQ-2952

## Coverage

Each of the seven requirements ADR-2370 addresses lands in exactly one task:
REQ-2940, REQ-2942, REQ-2948 and REQ-2950 in TSK-4300, REQ-2944 and REQ-2946
in TSK-4310, and REQ-2952 in TSK-4320. TSK-4300 alone tests the decision's
main claim, because a mistyped key that prints a line is what the decision
promises first. TSK-4320 touches only `meow-scm` and runs in parallel with
the other two.

## Not covered

REQ-2954, REQ-3040 and REQ-3042, and trust for a profile from an unfamiliar
repository, because ADR-2370 leaves all four to later decisions. I build no
detection for an absent profile: ADR-2370 says an absent profile resolves "by
detection, as before", and the tree has no detection to keep, since SPC-1040
reports every verb unresolved as `no profile`, so the epic keeps that.
