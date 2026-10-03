---
id: TSK-4965
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2680
closes: [REQ-3080, REQ-3084, REQ-3086, REQ-3090]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Answer whether the repository can be worked on, with `meow-checks doctor`

`meow-checks doctor` reports the profile's state, each verb's resolution in
each part and each installed pack's detection with the marker it matched,
marks each finding that depends on this machine, and writes nothing, as
SPC-1040 states under "Whether the repository can be worked on". It realises
ADR-2680. One task, one branch, one pull request, one review: the tests
first, then the change, its documentation and its marks.

## Acceptance criteria

Taken from ADR-2680's list of how it will be known realised:

1. Given a fixture repository with a `.markdownlint-cli2.yaml` and a
   `mise.toml`, and `meow-markdown` and `meow-mise` installed, when `doctor`
   runs, then it names each pack, the marker file it matched and the
   directory it sits in (REQ-3090). Closed by: a crate test naming REQ-3090,
   seen failing first.
2. Given a fixture whose `lint` verb names a tool not on `PATH`, when
   `doctor` runs, then that finding is marked `machine`, and it exits 3 where
   every finding is marked so (REQ-3084). Closed by: a crate test naming
   REQ-3084.
3. Given a fixture repository and state directory, when `doctor` runs, then
   both are byte-identical before and after, the ledger and any cache
   included (REQ-3086). Closed by: a crate test naming REQ-3086.
4. Given `doctor`'s output and `paw status`'s on the same fixture, when a
   test compares them, then `doctor` names no step, gate or artifact, and
   `paw status` names no verb resolution or pack detection (REQ-3080).
   Closed by: a crate test naming REQ-3080.

## What to do

Add `doctor` to the `verbs` feature of `crates/meow/`. Each installed pack
reports the markers it matched through its `status`, so add that line to
`meow-markdown`, `meow-mise` and `meow-gotask` where it is missing, and let
`doctor` read it without running any verb. Where `[parts]` isn't built yet,
report the root as the one part. Document the command on
`plugins/meow-checks/README.md` and add its failures to
`docs/troubleshooting.md`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

What `paw status` reports, which ADR-1170 and ADR-1210 decided, and a pack
that isn't installed, which can't report its marker.
