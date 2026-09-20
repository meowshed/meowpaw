---
id: RES-0060
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:brainstorm`

## Summary

Brainstorming is a named phase before any code, and its mechanism is the
sectioning: a design presented whole is approved whole, and a design presented
in sections is argued with. So the output is a sequence of checkpoints rather
than a document, the turn stops after each section, and the command writes
nothing - its output feeds the requirements or design step.

Where a rough idea is refined before it becomes a requirement. One of five
practice commands, each with its own document:
[RES-0156-options-command.md](RES-0156-options-command.md),
[RES-0157-grill-command.md](RES-0157-grill-command.md),
[RES-0158-decide-command.md](RES-0158-decide-command.md) and
[RES-0159-learned-command.md](RES-0159-learned-command.md).

The judgement behind all five is in
[RES-0029-research-technique.md](RES-0029-research-technique.md) and
[RES-0018-dev-log.md](RES-0018-dev-log.md); this is the surface.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## The surface

```text
/meow:brainstorm <rough idea>
```

From superpowers, where brainstorming is a named phase before any code: refine
by asking, explore alternatives, **present the design in sections for
validation**.

The sectioning is the mechanism. A design presented whole gets approved whole; a
design presented in sections gets argued with. For a command this means the
output is not one document but a sequence of checkpoints, and the stopping point
is after each section rather than at the end.

Writes nothing by default - it feeds `requirements` or `design`.

## What it must refuse

To write an artifact. A command that leaves a document in the tree with no
authorising record has created something the corpus cannot account for, and the
next step cannot tell a brainstorm from a decision by looking at the file.

To answer its own questions. The value is in asking; a session where the model
refines the idea by assuming what the person meant has produced a plausible
idea that is not theirs.

## Conclusions

1. The design is presented in sections and the turn stops after each,
   because a design presented whole is approved whole and a design presented in
   sections is argued with.
2. It writes nothing. Its output feeds the requirements or design step.
3. It refines by asking rather than by assuming, so what emerges is the
   person's idea rather than a plausible one.
4. It is optional to install and no step may require it.

## Sources

All read 2026-09-20.

- [obra/superpowers](https://github.com/obra/superpowers) - brainstorming as a
  named phase before any code, refining by asking, and presenting the design in
  sections for validation.
- [RES-0029-research-technique.md](RES-0029-research-technique.md) - the
  judgement this command packages.
