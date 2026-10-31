---
id: BUG-1740
artifact: bug
status: approved
severity: major
violates: REQ-4146
enters: implement
found: 2026-10-31
revised: 2026-10-31
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# One package with no trusted publisher stops the whole Pi release

`pi-release.yml` exits at the first package npm refuses with a 404, so every
package after it in the loop stays unpublished, and the message names no cause.

## Reproduction

Runs 41199967912 and 41217428814 of `pi-release.yml`, on 2026-10-31:

1. Dispatch `pi-release.yml` with `publish=true`, with `@meowshed/meow-csharp`
   on npm and naming no trusted publisher.
2. Read the step's output.

## What the system does

`meow-author` and `meow-checks` publish, `meow-code` and `meow-core` are already
there, and `npm publish` for `meow-csharp` fails with `E404` on the `PUT`. The
package exists, so the branch for a package never published doesn't match, and
the step exits 1. `meow-flow` and the 19 packages after it never run, so `meow-flow` on npm
stayed at 0.53.1 through two releases.

## What it should do, and why

REQ-4146 says a Pi package mirrors each unit and one unit tag releases both. A
refused package should be named with the command that fixes it and the loop
should go on, as it already does for a package never published, because one
package's missing setting says nothing about the others.

## Triage

Enters at implement, because REQ-4146 states the behaviour and the publish
step's loop breaks it. Major, because 21 Pi packages fell behind their Claude
units with only one cause reported. The packages themselves still need their
trusted publisher set, which takes the owner's npm login and no change here.

## Closed by

`tools/test_check_workflows.py::PublishLoop::test_a_refused_package_stops_no_other`
runs the step's own shell against a fake `npm`, and fails if the step stops at
the refused package or leaves it out of its final error.

## Plan

1. Treat every `E404` from `npm publish` as a package left over in
   `.github/workflows/pi-release.yml`, naming `npm trust` where the package exists.
