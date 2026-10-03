---
id: TSK-5020
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-0080, REQ-0086, REQ-0088]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Run the method's steps on a repository with no pack installed

A fixture repository with only the kernel and the method units installed runs
`paw ready`, `paw check` and `meow-checks status` to a result, every verb
reported unresolved and nothing waiting on a pack, as SPC-1080 states under
"What stays optional" and SPC-1090 under "The steps". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository with a profile declaring no verb and no pack's plugin directory reachable, when `meow-checks status` runs, then all five verbs are reported unresolved with their kind and nothing is reported passed (REQ-0086, REQ-0088). Closed by: a test under `plugins/meow-flow/tests/` naming REQ-0088, seen failing first.
2. Given the same fixture with an approved decision, when `paw ready spec` and `paw ready epic` run, then each exits as it would with every pack installed (REQ-0088). Closed by: a test naming REQ-0088.
3. Given a fixture task that produces only a specification change, when `paw ready implement` and `paw check` run, then the task passes through the same gate as one that changes code (REQ-0080). Closed by: a test naming REQ-0080.

## What to do

Build the fixture from the units' own files under a temporary directory, with
no pack's directory on any path the launchers search. Read the method's step
files and confirm none names a pack's command as required, fixing any that
does in the same change.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

A run with a model, which this repository keeps out of CI, so the fixture
drives the programs the steps call and not the steps' prose.
