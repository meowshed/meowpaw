# meow-core

`meow-core` is the kernel of the `meowpaw` harness. It ships one thing: the
shape of every reply Claude Code makes to you.

## What you get

Replies lead with the command, the path or the line. A failure arrives as its
cause, its location and its fix, with no dismay in front of it. Nothing opens
by announcing what is about to happen, and nothing closes by recapping it or
offering further help. Where a run stops, the last line names the command that
resumes it.

Nothing is dropped for the sake of brevity. A verification report keeps every
verb, a review keeps every finding, a gap list keeps every question, and a
hedge that carries real uncertainty stays, because deleting it manufactures
confidence you have not earned.

## What it costs you

While `meow-core` is enabled, its style replaces the output style you selected
for yourself. That is deliberate: a reply shape that a person can switch off is
switched off in the report that most needs it. Your recourse is to disable the
plugin, which takes the rest of the harness with it.

It keeps the platform's own software engineering instructions, so you lose none
of them by enabling it.

## Install it

```bash
claude plugin marketplace add meowshed/meowpaw
claude plugin install meow-core@meowpaw
```

Check what you got:

```bash
claude plugin details meow-core@meowpaw
```

## Where the rules come from

The decision is `project/adrs/ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md`,
and the part it creates is specified in `project/specs/SPC-1000-the-reply-shape.md`.
Read the decision for the alternatives and what would reverse it.
