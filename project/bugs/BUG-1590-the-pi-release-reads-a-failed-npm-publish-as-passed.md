---
id: BUG-1590
artifact: bug
status: approved # draft, approved, or withdrawn; open and closed are derived
severity: major # the registry held no version the workflow reported as published, so a release read as complete while half of one distribution shipped nothing
violates: REQ-4146 # a Pi package mirrors each unit one to one; a unit release must reach npm, which the workflow promises and the shell swallows
enters: implement # the step it enters at: implement or design where it violates a requirement, requirements where the requirement is wrong or none covers it, research where the cause is unknown
found: 2026-10-11
revised: 2026-10-11
issue: # the tracker's number, where the repository uses one
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi release reads a failed npm publish as passed

The Pi Release workflow's "Publish each package to npm" step runs
`if ! (cd "$pkg" && npm publish …) 2>&1 | tee /tmp/publish.log`, and the shell
tests the pipeline's exit status, which is `tee`'s. npm can fail and the step
stays green, so a run reports a release that npm never received. The wave of
2026-10-11 published fourteen packages that all failed this way: every job
concluded `success` while `npm view` found none of the versions.

## Reproduction

Seen at `c9011581` (`feat!: name the shared executable paw (#1049)`), Pi
Release run 38128969385, job "Publish each package to npm", on
`ubuntu-26.04` with npm 11.19.0 and trusted publishing (OIDC, no stored
token).

1. Push a tag `meow-<unit>-v<version>` whose npm version is missing, where the
   registry rejects the publish (a package without its trusted publisher
   configured answers E404 on the PUT).
2. Watch the workflow: the step prints npm's error and finishes 0, because
   `tee` exits 0 whatever npm exits.
3. The job concludes success; `npm view @meowshed/<unit>@<version>` answers
   E404.

## What the system does

The publish fails and the workflow reports it as passed:

```text
release  Publish each package to npm  npm error code E404
release  Publish each package to npm  npm error 404 Not Found - PUT https://registry.npmjs.org/@meowshed%2fmeow-prose - Not found
release  Publish each package to npm  npm error 404  The requested resource '@meowshed/meow-prose@0.6.0' could not be found or you do not have permission to access it.
```

The run concluded `success` in the Actions log of run 38128969385, and the
registry held only 0.5.1 afterwards. Fourteen packages published nothing that
day while seven Pi Release and Claude Release runs read as green.

## What it should do, and why

A publish that fails fails the step, because a gate that reads a failed verb
as passed is the failure this repository's principles name first: unresolved
is not a pass. REQ-4146 has each Pi package mirror its unit, and the release
that promises both registries keeps that promise only where npm's exit status
decides. The `tee` was there to show npm's output and to let the "cannot
publish over the previously published" reply mean a publish that already
happened; both survive a capture that tests npm's own status.

## Triage

Enters at implement: the step's shell logic is wrong, not its requirement.
Severity major, because a release reads as complete while half of one
distribution shipped nothing, and only a person running `npm view` by hand
finds it.

## Closed by

The reproduction, now passing: re-pushing a tag whose publish is rejected by
the registry fails the step, and one whose publish lands ends the step with
`+ @meowshed/<unit>@<version>`. The regression check lives in
`tools/test_check_workflows.py`, which reads the step's shell and refuses the
pipe that hides npm's status.

## Tasks

- [x] T-001 TSK-5430 Make the npm publish step fail when npm fails
      (`.github/workflows/pi-release.yml`)
