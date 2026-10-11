---
id: BUG-1630
artifact: bug
status: approved
severity: major
violates: REQ-4108
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pi injects a stale copy of the style, which lacks the secrets rule

The `meow-core` Pi package injects its own bundled `prompts/reply-shape.md`
where REQ-4108 says the reply shape `meow-core` provides as
`output-styles/meow.md` is injected, and the copy has drifted from the style
the plugin ships: it lacks R11, the secrets rule, and its R10 wording is an
older revision, so every Pi reply runs under a style the unit no longer ships.

## Reproduction

Seen with Pi 1.1.0, `@meowshed/meow-core` at the installed 0.9.0, at revision
`a42e16d2`.

1. Compare `packages/meow-core/prompts/reply-shape.md` with
   `plugins/meow-core/output-styles/meow.md`.

## What the system does

The two differ: the bundled copy carries no R11, and its R10 names the
`${CLAUDE_PLUGIN_ROOT}` path the copy replaced. The extension injects the
bundled copy on every `before_agent_start`, so the drift reaches every reply.

## What it should do, and why

REQ-4108 says the reply shape `meow-core` provides as `output-styles/meow.md`
is what Pi injects. A bundled copy is how REQ-4130 forces it to ship, but a
copy nothing holds to the source is a second standard that drifts, and the
drift already dropped a rule that must hold.

## Triage

It enters at implement: the copy exists, and the fix is to carry the style
over and hold the copy to the source with a check. Severity is major, because
the style governs every reply on the platform and one of its must-hold rules
is absent.

## Closed by

`tools/test_pi_extensions.py` fails while the copy differs from the style
beyond the platform's path phrasing, and passes once the copy carries the
style and the check holds them equal.

## Tasks

- [ ] T-001 TSK-5490 carry the style into the bundled copy and hold the copy
      to the source with a check, in `packages/meow-core/prompts/` and
      `tools/test_pi_extensions.py`
