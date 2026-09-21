---
id: BUG-1040
artifact: bug
status: approved
severity: critical
violates: REQ-0930
found: 2026-09-21
revised: 2026-09-21
issue: 28
---

# The forced style is not applied, so the reply shape is opt-in

## Reproduction

On Claude Code 2.1.278, with `meow-core` 0.3.0 enabled at user scope and
`force-for-plugin: true` in `plugins/meow-core/output-styles/meow.md`:

```text
$ claude plugin list
  ❯ meow-core@meowpaw   Version: 0.3.0   Scope: user   Status: ✔ enabled

# a new session, in a directory other than meowpaw
/output-style
Output style: default
- default (current)
- meow-core:meow: The reply shape the meowpaw harness imposes on every reply
```

Before recording this we checked the field's spelling and meaning against the
platform's own documentation, looked for a competing `outputStyle` setting at
user and project level, and re-synced the installed version with the manifest.
None of the three explains the behaviour.

## What the system does

The plugin loads and the style is discovered, which the listing shows. The
style is not applied. A person who does not run `/output-style meow-core:meow`
gets the platform default, in every session, in every repository.

## What it should do, and why

REQ-0930 requires one shape on every reply, unconditionally, with no plugin,
skill or step exempt. REQ-0932 requires the kernel to carry it so that a
repository installing any part of the harness receives it.

The platform's documentation for output-style front matter states that
`force-for-plugin` applies a plugin's style "automatically whenever the plugin
is enabled, without requiring users to select it" and that it "overrides the
user's `outputStyle` setting". On this version it does neither.

The reason unconditionality was load-bearing is written in ADR-1000: a shape
some replies follow guards nothing, because the report that hides the
unresolved verb is the report that gets approved.

## Triage

This is not an implementation defect in the plugin. The file is correct against
the documented contract, and the contract is not honoured.

It routes to design. ADR-1000 chose a forced output style because
`force-for-plugin` was the only field the platform offered that holds a style
without each person opting in. That premise is false on this version, so the
decision rests on a mechanism that does not deliver what it claims, and the
alternatives need comparing again.

## Closed by

Not closed. One of two things closes it:

- The style applies without selection, on a version where the documented
  behaviour works, with the observation recorded.
- ADR-1000 is amended, or superseded, by a decision whose mechanism holds. A
  candidate it never considered is a `SessionStart` hook, whose
  `additionalContext` reaches the model at the start of every session and does
  not depend on the style system. RES-0203 records the hook, and no research
  compares it against a style for this purpose.

Until then, EPC-1000 is not realised: its first acceptance criterion is that a
repository installing the kernel receives the shape without selecting it.
