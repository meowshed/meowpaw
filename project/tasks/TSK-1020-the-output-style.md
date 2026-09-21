---
id: TSK-1020
artifact: task
status: approved
revised: 2026-09-21
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
issue: 6
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

Closed by `b228817`, at that revision:

```text
$ /reload-plugins
Reloaded: 5 plugins · 3 skills · 6 agents · 0 hooks

$ /output-style
- meow-core:meow: The reply shape the meowpaw harness imposes on every reply
  it makes to a person.

$ /output-style meow-core:meow
Output style set to meow-core:meow
```

Every reply in this session since has been produced under it, leading with the
action and closing with the next step rather than an offer of help.

The style was selected by hand here because the session predates the file.
`force-for-plugin: true` applies it without that step in a session that starts
after it, which no run has observed yet.

## Left alone

This task says nothing about verb resolution, and names none of the harness's
not-working states: EPC-1000 defers REQ-2774 to the decision that creates verb
resolution.
