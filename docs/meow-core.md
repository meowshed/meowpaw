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

## Subordinate agents

A subordinate agent runs its own system prompt, and an output style never
reaches it. If you write a prompt that dispatches one, include the style's
`<rules name="the reply shape">` block from
`${CLAUDE_PLUGIN_ROOT}/output-styles/meow.md` in it as it stands, and the
subordinate answers in the same shape. A fork inherits the style and needs
nothing.

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

## Measure it

The shape is measured by running its cases with the plugin and without it. Each
run is a real model call, so nothing runs it automatically. You run it by hand:

```bash
mise run eval                              # Sonnet 5 and Opus 5.5, judged by Opus 5.5
mise run eval -- --model claude-haiku-4-5-20251001  # the same cases on one other model
```

Each unit prints a table with the difference the plugin makes on each case and
what its text costs in tokens. A fall in that difference is a regression. A
fall in the absolute score isn't, because a weaker model lowers both arms.

Run it again when a new model comes out. A rule written to correct an older
model's habit becomes dead weight once the new model stops having that habit,
and only a run on the new model shows which rules those are.

A usage limit or a cost ceiling shows up as a run error in the table, and never
as a lower score.

## Where the rules come from

The decision is `project/adrs/ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md`,
and the part it creates is specified in `project/specs/SPC-1000-the-reply-shape.md`.
Read the decision for the alternatives and what would reverse it.
