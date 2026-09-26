# meow-prose-gate

`meow-prose-gate` stops Claude Code from publishing a text that carries a
defect any reader can point to. It reads a commit message, a pull request or
issue body, a comment, a review and release notes before the command runs, and
it installs on its own, with no other part of the `meowpaw` harness.

## What it blocks

The gate blocks three defects and nothing else, because a block another reader
would dispute teaches you to route around it:

- an idiom from a fixed list of fifteen, such as "low-hanging fruit" or "under
  the hood", which the gate's prompt in `hooks/hooks.json` names in full
- a bold fragment standing in for a heading
- a text hidden behind a file, such as `git commit -F notes.txt` or
  `--body-file`, which the gate can't read

Unexplained acronyms and American spellings are left to the writing skill and
the reviewer in `meow-prose`. Haiku 4.5 judged both backwards: it passed the
defect and blocked the correction, in the measurement recorded in
`project/tasks/TSK-1140-the-prose-gate.md`.

When the gate blocks, Claude Code gets the reason as the command's error, with
the span and the fix, and publishes again with the text corrected. A text given
inline or in a heredoc passes the check on hidden files, so `git commit -F -`
with a heredoc is fine.

## What it costs you

One call to Haiku 4.5 each time Claude Code runs a command that publishes text:
`git commit`, and `gh` creating or editing a pull request, an issue, a comment,
a review or a release. Every other command runs without it. Each call has a
timeout of 60 seconds, and a call that times out lets the command through, so
a text too long for Haiku 4.5 to read in 60 seconds passes unread.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-prose-gate@meowpaw
```

The gate carries its own criteria and needs no other plugin: neither
`meow-prose`, the writing standard, nor `meow-core`, the harness's kernel. With
`meow-prose` installed as well, the writing skill shapes the text before it is
written and the gate catches what the skill missed.

## Where the rules come from

The decision is the architecture decision record
`project/adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md`,
as amended by
`project/adrs/ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md`,
and the unit is specified in `project/specs/SPC-1010-the-writing-standard.md`.
