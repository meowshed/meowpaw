# meow-prose

`meow-prose` holds everything Claude Code writes for you to one writing
standard: documents, commit messages, pull request and issue bodies, review
comments, code comments and replies. It installs on its own and needs no other
part of the `meowpaw` harness.

## What you get

A skill that loads before Claude writes, so the standard shapes the first draft
instead of a rewrite afterwards. It asks for the answer first and the reason
beside it, one term for one thing, sentences a second-language reader can
follow, and the skeleton each kind of document needs. It also lists the shapes
of text to rewrite on sight, such as a bold sentence opening a paragraph or an
opener announcing how many items follow, each with a failing and a corrected
example.

The standard is British English unless your repository declares another
language. To declare one, add it to `.meowpaw/profile.toml`:

```toml
[prose]
language = "en-US"
```

Claude then writes that language across the repository. A technical term
keeps the spelling its own domain uses, and a quotation keeps its author's
wording, whatever you declare.

## What it costs you

The skill's description sits in context on every turn so that Claude knows when
to load it, which costs about 440 characters. When it loads, the skill itself
costs about 4,800 tokens on Sonnet 5. The pattern catalogue, the document
skeletons and the self-review checks sit in separate files that load only when
Claude needs them.

Claude doesn't yet load the skill on its own when you ask for a commit message
or a pull request description. Until the plugin ships a hook that loads it,
invoke it with `/meow-prose:writing` before you ask for the text.

## Install it

```bash
claude plugin marketplace add meowshed/meowpaw
claude plugin install meow-prose@meowpaw
```

Check what you got:

```bash
claude plugin details meow-prose@meowpaw
```

## Where the rules come from

The decision is
`project/adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md`,
and the part it creates is specified in
`project/specs/SPC-1010-the-writing-standard.md`. Read the decision for the
alternatives and what would reverse it.
