---
id: TSK-1020
artifact: task
status: draft
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes:
  [
    REQ-0930,
    REQ-0933,
    REQ-0934,
    REQ-0936,
    REQ-0938,
    REQ-0940,
    REQ-0942,
    REQ-0944,
    REQ-0946,
    REQ-0948,
    REQ-0950,
    REQ-0952,
  ]
issue:
---

# Write the output style that carries the reply shape

One task, one branch, one pull request, one review.

## What to do

Write the style file in `plugins/meow-core/output-styles/`, with front matter
setting `keep-coding-instructions: true` and `force-for-plugin: true`, and a
body carrying the eight rules and the condition under which each yields, as
ADR-1000's table states them.

The rules, each with the requirement it closes:

| The rule                                                               | Closes                       |
| ---------------------------------------------------------------------- | ---------------------------- |
| One shape on every reply, with nothing exempt                          | REQ-0930                     |
| Lead with the command, the path or the line                            | REQ-0934                     |
| No announcing opening, no closing recap, no offer of further help      | REQ-0944, REQ-0946, REQ-0948 |
| Progress states step, pending and unresolved, computed from the record | REQ-0936                     |
| A failure gives cause, location and fix, with no dismay before it      | REQ-0938, REQ-0940           |
| A stop names the command that resumes it                               | REQ-0942                     |
| Completeness outranks brevity, and the answer wins over the shape      | REQ-0950, REQ-0952           |
| The pre-send check, ending in the first-line and last-line test        | REQ-0933                     |

Write it in the form it should produce (REQ-1115): prose that states reasons,
with obligations structurally distinguishable from explanation (REQ-1120), in
one structural vocabulary (REQ-1112).

Write the documentation page for the kernel in `docs/` in the same change, so
that verification covers it.

## Depends on

TSK-1010, because the style ships inside the plugin and has nowhere to live
before the plugin exists. The dependency is structural and not a matter of
convenience.

## Evidence

The style in force in a repository with only `meow-core` installed, with the
command that shows it, its output and the revision. A reply produced under it
that leads with an action and closes without an offer of help.

## Left alone

This task says nothing about verb resolution, and names none of the harness's
not-working states: EPC-1000 defers REQ-2774 to the decision that creates verb
resolution.
