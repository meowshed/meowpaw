# meow-prose-gate

`meow-prose-gate` stops Claude Code from publishing a text that carries a
defect any reader would name. It reads a commit message, a pull request or
issue body, a comment, a review and release notes before the command runs, and
it installs on its own, with no other part of the `meowpaw` harness.

## What it blocks

The gate blocks five defects and nothing else, because a block another reader
would dispute teaches you to route around it:

- an idiom or a saying, such as "low-hanging fruit"
- an acronym never expanded in the text, apart from ones every engineer reads,
  such as API or JSON
- an American spelling in prose, apart from a technical term, an identifier, a
  command and a quotation
- a bold fragment standing in for a heading
- a text hidden behind a file, such as `git commit -F notes.txt` or
  `--body-file`, which the gate can't read

When it blocks, Claude gets the reason as the command's error, with the span
and the fix, and publishes again with the text corrected. A text given inline
or in a heredoc passes the last rule, so `git commit -F -` with a heredoc is
fine.

## What it costs you

One call to Haiku 4.5 each time Claude runs a command that publishes text:
`git commit`, and `gh` creating or editing a pull request, an issue, a comment,
a review or a release. Every other command runs without it. Each call has a
timeout of 60 seconds. A call that times out lets the command through, so a
very long text can pass unread.

## Install it

```bash
claude plugin marketplace add meowshed/meowpaw
claude plugin install meow-prose-gate@meowpaw
```

The gate carries its own criteria and needs neither `meow-prose` nor
`meow-core`. With `meow-prose` installed as well, the writing skill shapes the
text before it is written and the gate catches what got through.

## Where the rules come from

The decision is
`project/adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md`,
as amended by ADR-1020, and the unit is specified in
`project/specs/SPC-1010-the-writing-standard.md`.
