---
id: TSK-4380
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2470
closes: [REQ-2784, REQ-2786, REQ-2788, REQ-2790, REQ-2792]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Point the design step at the threat model and hold the model's form

The design step's rule D20 sends a decision with a security-relevant boundary
to the threat model in SPC-1080, and a fixture holds that model to the form
ADR-2470 sets: STRIDE's six categories each mapped, an accident by the harness
first, every trust boundary listed and every threat ranked in words. One task,
one branch, one pull request, one review: the tests first, then the change,
its documentation and its marks.

## Acceptance criteria

1. Given SPC-1080's "The threat model", when a fixture reads it, then it
   names Spoofing, Tampering, Repudiation, Information disclosure, Denial of
   service and Elevation of privilege, each with a control or `None`
   (REQ-2786). Closed by: a fixture naming REQ-2786, seen failing first
   against a copy with one category removed.
2. Given that section, when a fixture reads its first ranked threat, then the
   threat names the harness as its actor (REQ-2784, REQ-2792). Closed by: a
   fixture naming both.
3. Given that section, when a fixture reads it, then it holds a table of
   trust boundaries and each threat's likelihood and impact is one of
   `likely`, `unlikely`, `severe` and `minor`, with no digit in either column
   (REQ-2788, REQ-2790). Closed by: a fixture naming both.
4. Given `plugins/meow-flow/skills/method/steps/design.md`, when a fixture
   reads rule D20, then it says a decision with a security-relevant boundary
   updates the threat model the repository's specification keeps, and it
   names no identifier of this repository. Closed by: a fixture naming
   ADR-2470.

## What to do

Add the pointer to rule D20 in the design step file, with its reason, and hold
the file to SPC-1030 and `plugins/meow-flow/budget.toml`. The step file ships
to every repository, so the pointer names the threat model by its subject and
never as SPC-1080, which only this repository holds.

Add the fixtures for criteria 1 to 3 beside `tools/test_record_shape.py`,
because they read this repository's record and not a unit's behaviour, and
read the section by its heading, so they fail when it moves or loses a
category.

## Depends on

Nothing.

## Evidence

Closes REQ-2784, REQ-2786, REQ-2788, REQ-2790 and REQ-2792. `ThreatModel` in
`tools/test_threat_model.py` closes criteria 1 to 3 in five checks, reading
SPC-1080's "The threat model" by its heading. They failed against copies of
the section with a category removed, a placeholder control, a boundary
dropped or left unnamed, an attacker's threat ranked above an insider's and a
digit in a rank, and one check holds that a removed category and a
placeholder control are found. `ThreatModelPointer` in
`plugins/meow-flow/tests/test_record.py` closes criterion 4 in two checks,
and the first failed at the pull request's first commit, before D20 named
the threat model. Two reviewing agents found checks that would pass a wrong
model or a wrong D20, and the pull request rewrote them in commits of their
own. `meow-checks run format lint check test build` passed all five verbs,
`mise run all` exited 0 and `paw check` reported 0 findings, each on the tree
before this Evidence was last edited. The pull request is #825.

## Left alone

The threat model's content, which the spec step wrote in this pull request
and which changes in the pull request of each later decision that adds a
trust boundary. A control for a threat the model marks uncovered, because
ADR-2470 leaves each to its own decision.
