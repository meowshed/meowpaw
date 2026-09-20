---
id: RES-0204
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0035, RES-0202
---

# The constitution

## Summary

The one document loaded into every session had no research of its own. Its
documented size limit exists for adherence and not for cost, because a longer
file is followed less well, and contradictory rules are resolved arbitrarily
and silently, which is worse than either rule alone. Splitting it into imports
saves nothing, because imports expand at launch; only a path-scoped rule
defers. And it is context, which enforces nothing, so the first question asked
of every line is whether a check could settle it.

Research for the one document the harness ships that is loaded into every
session whether or not it is needed. It is the most expensive real estate the
project has, and nothing owned it.

It covers what the platform charges for it and what it promises in return, and
what belongs in it and what does not. It also covers how it fails, and what a
repository's own constitution may contain that the harness's may not.

It does not cover its lifetime, which is
[RES-0035-vision.md](RES-0035-vision.md), nor the tiers it sits at the top of,
which are
[RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md).

## The question

Three of the surveyed harnesses have something like this and none says what
belongs in it. spec-kit writes a `constitution.md` once per project; the
internal repositories each document their process in a `CLAUDE.md`, and the
divergence between those six documents is what this whole project exists to
fix.

So the question is not whether to have one. It is what a document that is
always loaded has to earn, and what should be somewhere else.

## Method

We fetched and read the platform's memory documentation on 2026-09-20. It gave
the size target and its stated reason, the specificity and structure guidance,
and the arbitrary resolution of contradictions. It also gave the import
expansion and its depth limit, the rules directory and its path scoping, the
discovery order, and the stripping of block comments.

The surveyed harnesses were read for what each puts in its own instructions
file, which is the evidence that the six internal copies diverged.

Nothing was measured. The claim that a shorter constitution is followed better
belongs to the documentation, and nobody reproduced it here.

## Findings

### Context, and never configuration, which decides what belongs in it

The documentation states the category plainly: instruction files are _"context,
not enforced configuration"_, and to block an action regardless of what the
model decides, a hook is what does it.

So the constitution is a document of intentions that are usually honoured. A
rule that must hold every time is a check in the gate, a hook, or a rule the
project is choosing to hope for. Writing it in capital letters moves it between
none of those categories.

That gives the first question asked of every line: **could this be a check?**
If it could, it belongs in the gate, and the constitution at most names it.

### The size limit exists for adherence

The documented guidance is a _"target under 200 lines"_ per file, and the
stated reason is the interesting half: _"Longer files consume more context and
reduce adherence."_

That inverts the usual argument. A long constitution is not merely expensive;
it is followed less well than a short one. So trimming it is not an economy
measure taken against the document's effectiveness - it is the document's
effectiveness.

The same section gives three properties that work, and a draft can be measured
against all three, so none of them is a matter of taste:

- **Specific enough to verify.** _"Use 2-space indentation"_ rather than
  _"Format code properly"_; _"Run `npm test` before committing"_ rather than
  _"Test your changes"_.
- **Structured.** Headers and bullets, because _"Claude scans structure the
  same way readers do"_.
- **Consistent**, because _"if two rules contradict each other, Claude may pick
  one arbitrarily."_

That last one is the sharpest and the least obvious. A contradiction in a
constitution does not produce an error or a question. It produces a coin flip,
silently, differently each time - which is worse than either rule alone,
because the behaviour is now unreproducible.

So a constitution is checked for internal contradiction as a standing habit,
and two rules that pull against each other are resolved into one rule with its
exception stated.

### Splitting it into files saves nothing, and there is exactly one mechanism that does

`@path` imports are _"expanded and loaded into context at launch alongside the
CLAUDE.md that references them"_, recursively to four hops. A constitution
split into imports is organised, and it is no smaller.

The mechanism that actually defers is a rule in `.claude/rules/` carrying a
`paths` field. Without one it loads at launch _"with the same priority as
`.claude/CLAUDE.md`"_, and with one it loads only when the model works with
matching files.

So there are three honest placements for a rule the project wants:

| The rule applies                   | Where it goes      |
| ---------------------------------- | ------------------ |
| Always, to any work                | The constitution   |
| Whenever certain files are touched | A path-scoped rule |
| When a named activity happens      | A skill            |

And the platform's own advice for the third case is explicit: for
task-specific instructions that need not be in context all the time, use a
skill instead.

### Discovery is directional, and the last word goes to the nearest file

Instruction files are loaded from the working directory and every directory
above it, concatenated, so none overrides another, ordered from the filesystem
root down. The file closest to where the session started is read last. Personal
notes are appended after the shared file at each level.

Two consequences for a harness distributed to other people's repositories.

The harness's constitution is not the only one in the room. A repository
has its own, a monorepo has several, and the user has a personal one. What the
harness writes is one voice among them, and it is not the last.

A rule that depends on being read last cannot be relied on. Anything the
harness needs to be true regardless of what else is loaded is a check, and no
sentence carries it.

### It costs nothing to leave notes for maintainers

Block-level HTML comments are stripped before the content is injected, so a
note to whoever maintains the file is free. Comments inside code blocks are
preserved, and a direct read of the file shows everything.

That is a small finding with a real use. The reason for a rule sits beside it
for the human maintainer, and no session pays for it. That partly resolves the
standing tension between _a rule without its reason is applied wrongly_ and
_every line is a recurring cost_.

Partly, not wholly. The reason is what lets a reader apply a rule to a case its
author did not foresee, and the reader here is usually the model. So the
resolution is a judgement per rule: the reason is in the text where the rule is
likely to meet an unforeseen case, and in a comment where it is historical.

### What belongs in it

Read against everything above, a constitution earns its place with material
that is simultaneously always relevant, not checkable, and not derivable from
the repository:

- **What this project is**, in a sentence, because every other document assumes
  it. - **The standing prohibitions**, which are short, absolute and frequently
  the thing a later instruction will try to override. - **The vocabulary**,
  where the project uses a word in a way the model would otherwise read
  differently. - **Where things live**, because a path that has to be guessed
  is guessed wrongly once per session. - **The named exceptions**, since a
  method with no stated exception is worked around. - **What to do when
  something is missing** - the unresolved, absent, untrusted vocabulary -
  because that is the behaviour the method most depends on and the one a model
  is least inclined to.

### What does not belong in it

- **Anything a check can settle.** It belongs in the gate; the constitution may
  name the gate.
- **Anything specific to a language, a tool or a directory.** That is a pack or
  a path-scoped rule.
- **Procedure.** A sequence of steps is a command, invoked when the sequence is
  wanted.
- **Explanation of the method.** That is documentation, read once by a person.
- **Anything derivable from the repository**, since a rule restating what the
  files already show is wrong the first time the files change.
- **A rule nobody has broken.** This is the hardest to apply and the most
  valuable: a constitution accumulates by addition, and a line added for a
  failure that never recurred is paid for in every session forever.

### The harness's own constitution and a repository's are different documents

The harness ships method: what a requirement is, what a gate means, what is
never attributed. A repository's own carries its subject matter: what this
codebase is, what its conventions are, what its exceptions are.

Keeping them separate matters because they have different lifetimes and
different authors. A repository updates its own freely; the harness's changes
when the method changes, which should be rarely and always through a decision.

The initialisation step writes a repository constitution, and the distinction
bounds what it may put there: it records what the repository already is, and it
does not copy the method in.

### It is a living document with the same obligation as the others

It is a projection over the decisions about method, carrying no history of its
own, rewritten freely, because the history is in the decisions.

So the same obligation applies as to the specification: **updating it removes
as well as adds.** A constitution that only grows records every rule the
project ever wanted, loads it into every session, and most of it is no longer
true.

## Conclusions

1. The constitution is context and enforces nothing, so a rule that must hold
   every time is a check or a hook, and the constitution at most names it. 2.
   The first question asked of every line is whether a check could settle it. 3. It targets under 200 lines, because the documented consequence of length
   is reduced adherence and not cost alone. 4. Every rule is specific enough to
   verify, naming the command, the path or the value, and never the intention. 5. It is checked for internal contradiction, since contradictory rules are
   resolved arbitrarily and silently, which makes the behaviour unreproducible. 6. Two rules that pull against each other are merged into one with its
   exception stated. 7. Splitting it into imports saves nothing, as imports
   expand at launch. 8. A rule that applies only to certain files becomes a
   path-scoped rule, which is the only mechanism that defers loading. 9. A rule
   that applies to a named activity becomes a skill, following the platform's
   own division. 10. The harness's constitution is one of several loaded, and
   is not the last, so nothing that must hold depends on being read last. 11.
   Reasons for rules may sit in stripped comments where they are historical,
   and in the text where the rule will meet unforeseen cases. 12. It carries
   what is always relevant, not checkable, and not derivable: what the project
   is, the standing prohibitions, the vocabulary, where things live, the named
   exceptions, and what to do when something is missing. 13. It carries no
   procedure, no language-specific material, no explanation of the method, and
   nothing the repository already shows. 14. A rule is removed when the failure
   it prevents stops recurring, because an accumulating constitution is paid
   for in every session forever. 15. The harness's constitution and a
   repository's are separate documents with different authors and lifetimes,
   and initialisation does not copy the method into the repository's. 16.
   Updating it removes as well as adds, since it projects the current decisions
   and records none of the past ones.

## Sources

All read 2026-09-20.

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) -
  instruction files loaded at the start of every session and treated as
  context, which enforces nothing, with a hook as what blocks an action; the
  200-line target with reduced adherence as the stated reason; the specificity
  and structure guidance with its worked examples; that contradictory rules may
  be resolved arbitrarily; `@path` imports expanded at launch to four hops;
  `.claude/rules/` loading at launch without `paths` and only on matching files
  with it; the instruction to use skills for task-specific material; root-down
  concatenation with the nearest file read last and personal notes appended
  after shared ones; and block-level HTML comments stripped before injection. -
  [RES-0035-vision.md](RES-0035-vision.md) - the constitution as one of three
  living projections, over decisions about method, carrying no history of its
  own. -
  [RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md) -
  the six tiers, the rule that the first question is whether a program could
  settle the instruction, and what may not move down a tier. -
  [RES-0058-init.md](RES-0058-init.md) - that initialisation writes a profile
  and a constitution and proposes everything else. -
  [RES-0003-external-harnesses.md](RES-0003-external-harnesses.md) - spec-kit's
  `constitution.md` written once per project, and its `analyze` step reporting
  constitution conflicts as one of six defect categories.
