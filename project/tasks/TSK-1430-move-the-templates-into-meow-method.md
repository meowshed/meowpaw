---
id: TSK-1430
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1100
closes: [REQ-0526, REQ-0528]
issue: 190
---

# The templates, shipped with meow-method and overridable

One task, one branch, one pull request, one review.

## What to do

Move `templates/*.md` to `plugins/meow-method/templates/`, correct their citations of the old requirement scheme, such as `[R-H-058]`, to the requirements in force, and change `CLAUDE.md`'s layout section to say where the templates are. Show that `meow-method template <kind>` prints the unit's template, and the repository's where `.meowpaw/templates/<kind>.md` exists.

## Depends on

TSK-1420, because `template` resolves the path this move creates.

## Evidence

Not yet.

## Left alone

The content rules each template states, which later decisions revise.
