---
id: TSK-5050
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2555
closes: [REQ-0343, REQ-3040, REQ-3046]
issue: 987
projected: 86b30e9da05d
tracked: e9b7bfbe54fe
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Read the parts a repository declares, and layer a part's profile over the root's

The profile reader in `crates/meow/` reads `[parts]` from the root profile
and, for a part whose directory holds `.meowpaw/profile.toml`, reads that
file over the root's, as SPC-1080 states under "The profile". One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a root profile declaring parts `site` at `site/` and `crate` at
   `crates/x/`, when any command reads the profile, then it knows both parts
   and their directories, and `parts` isn't reported as an unknown key
   (REQ-0343). Closed by: a crate test naming REQ-0343, seen failing first.
2. Given a part whose profile sets `[verbs] test` and leaves out `lint`, when
   the reader resolves that part, then `test` is the part's command and
   `lint` is unresolved there, never the root's (REQ-3040). Closed by: a
   crate test naming REQ-3040.
3. Given a part's profile carrying `[record]` or `[parts]`, when the reader
   reads it, then each is reported as an unknown key and the root's record
   and parts stand (REQ-3046). Closed by: a crate test naming REQ-3046.
4. Given a root profile with no `[parts]`, when the reader runs, then the
   repository is one part, its root, and every existing profile test passes
   unchanged. Closed by: the crate's existing profile tests.

## What to do

Add `[parts]` to the profile module, one entry per part with its name and
directory, and the layering SPC-1080 states: a key the part declares
replaces the root's for that part, and a verb the part's `[verbs]` leaves
out is unresolved in that part. Add `parts` to the table of keys in
`crates/meow/src/profile.rs` with its reason. Read the profiles in the tool
itself and rely on no setting the platform inherits from a parent directory.
Document `[parts]` on `plugins/meow-checks/README.md`, the unit whose verbs
it changes.

## Depends on

Nothing.

## Evidence

The crate tests in `crates/meow/src/profile.rs` close the criteria, each seen
failing against the reader without `parts` in the table of keys and without
the layering. `the_root_profile_declares_its_parts` and
`a_part_outside_the_repository_is_reported` close criterion 1 (REQ-0343).
`a_part_declares_its_own_stages_and_takes_none_from_the_root` and
`a_parts_broken_profile_is_unparseable_and_names_its_file` close criterion 2
(REQ-3040). `a_parts_record_and_parts_are_unknown_and_the_roots_stand` closes
criterion 3 (REQ-3046). The crate's existing profile tests, unchanged and
passing, close criterion 4.

A part whose directory holds no profile of its own reads the root's, a choice
I made because SPC-1080 layers a part's profile only where one exists.

Every stage passed in pull request #1072.

## Left alone

How `meow-checks` reports a part, which TSK-5055 does, and how a pack finds
its marker, which TSK-5060 does.
