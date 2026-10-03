---
id: TSK-5000
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2545
closes: [REQ-2252]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Add the seven questions to the spec template, and the concerns to the design and spec steps

The `spec` template carries a section of seven fixed questions, each answered
or marked `unanswered`, the design step names a decision's concerns in
`concerns:`, and the spec step frames each in a section whose heading names
it, as SPC-1090 states under "The questions a specification answers". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `paw template spec`, when its file is read, then it carries one section listing the seven questions SPC-1090 names, each with `unanswered` as its placeholder (REQ-2252). Closed by: a test under `plugins/meow-flow/tests/` naming REQ-2252, seen failing first.
2. Given `paw template adr`, when its front matter is read, then it carries an optional `concerns:` list, and a decision with `concerns: [security]` passes the front matter check. Closed by: a crate test.
3. Given `steps/design.md` and `steps/spec.md`, when a test reads them, then the first tells the step to name each concern in `concerns:` and the second to frame each in a section whose heading names it. Closed by: a test under `plugins/meow-flow/tests/`.

## What to do

Edit `plugins/meow-flow/templates/spec.md`, `templates/adr.md`,
`skills/method/steps/design.md` and `skills/method/steps/spec.md`, and add
`concerns` to the decision kind's fields in `plugins/meow-flow/lib/layout.toml`
as optional, so approved decisions with none still pass. Hold the change to
SPC-1030 and the unit's `budget.toml`, and document both on
`plugins/meow-flow/README.md`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The specifications under `project/specs/`, which TSK-5010 changes, so they lack
the section until it lands.
