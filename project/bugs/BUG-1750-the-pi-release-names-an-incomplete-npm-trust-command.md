---
id: BUG-1750
artifact: bug
status: done
pr: 1151
severity: minor
violates: REQ-4146
enters: implement
found: 2026-10-31
revised: 2026-10-31
issue: 1150
projected: 80830cfe83f2
tracked: 8ca894f78a7a
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi release names an `npm trust` command that npm refuses

The error `pi-release.yml` prints for a package with no trusted publisher omits
`--allow-publish`, so a person who runs it gets a second error.

## Reproduction

npm 11.19.0, logged in as the package's owner:

1. Run `npm trust github @meowshed/meow-go --file pi-release.yml --repo meowshed/meowpaw --yes`.

## What the system does

npm exits with `At least one permission flag is required (--allow-publish,
--allow-stage-publish)`, and sets no trusted publisher.

## What it should do, and why

REQ-4146 needs each package to reach npm, and this message is how a package with
no trusted publisher gets there. It should name a command npm accepts.

## Triage

Enters at implement, because REQ-4146 states the behaviour and only the message
breaks it. Minor, because npm's own error names the missing flag.

## Closed by

`tools/test_check_workflows.py::PublishLoop::test_a_refused_package_stops_no_other`
now asserts the command carries `--allow-publish`.

## Plan

1. Add `--allow-publish` to the command the message names in
   `.github/workflows/pi-release.yml`.
