---
id: RES-0027
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The writing standard

## Summary

The two dominant style guides agree closely enough that their intersection is a
usable baseline, and one internal skill already implements it. The findings are
about placement, and style settles none of them. The standard is loaded in
every conversation, because a commit message and a chat reply are both prose.
Every decision in it carries its reason where a reader judging applicability
will look. And it teaches by showing a failing sample beside its fix, where
describing the failure teaches nothing.

Research for `technical-english` in `meow-prose` - the standard that governs
every word the harness produces. This is about voice and sentence craft;
[RES-0020-documentation.md](RES-0020-documentation.md) covers document types, and
[RES-0005-skill-format.md](RES-0005-skill-format.md) covers what a skill costs.

## Method

Both published style guides were fetched and read directly on 2026-09-20,
along with the plain-English guidance, and read against each other so the
intersection could be taken rather than one adopted.

We read the internal writing skill in full from its working tree. The argument
that it is the most effective and the most expensive internal artifact depends
on its length as well as its content.

Nothing was measured. The claim that this skill has needed the fewest
corrections in use is an impression reported by its author's repository rather
than a count made here, and is recorded as such.

## Why this is load-bearing rather than decorative

`meowctl` loads its writing skill in **every conversation, before anything is
written**, on the stated grounds that a commit message is prose and a chat
reply is prose. That is an unusual position and the evidence supports it: it is
the internal artifact that has needed the fewest corrections in use, and the
observable effect is that its specifications state reasons.

The mechanism is not mysterious. Style propagates - the formatting and voice of
a prompt shape what the model produces. A standard loaded before work begins is
therefore not a polish pass; it changes what gets written in the first place.

## The failure it exists to prevent

`meowctl`'s skill contrasts two samples of the same facts. The first has an
author who made a choice, a reader who might need the fast path, and a reason
for the trade-off. The second states the same facts as truths handed down by
nobody in particular, in short inverted sentences with no reasons attached.

The grammar of both is fine. The second is what most harness prompts and most
generated documentation read like, and its name in that skill is a **philosophy
treatise**.

Two things go wrong with it. A reader cannot tell whether a rule applies to
their case, because the reason that would let them judge is missing - so it is
applied literally, including where it is wrong. And a model reading it produces
more of it, which is how a whole repository ends up written in scripture voice.

## What the big style guides agree on

Google and Microsoft converge, and the intersection is the safe default. Second
person, active voice with the actor named, present tense, sentence case for
headings, and the serial comma. Numbered lists for sequences, code font for
code, and writing for a reader whose first language is not English.

Microsoft's brevity rules are the sharper half and the ones that change text
most:

- **Bigger ideas, fewer words.** Shorter is better.
- **Write like you speak.** Read it aloud. Contractions are correct.
- **Get to the point fast.** Front-load what matters; make the next step
  obvious.
- **Revise weak writing.** Start statements with a verb. Cut "you can" where it
  adds nothing. Avoid "there is", "there are", "there were".

"You can access Office apps across your devices, and you get online file
storage and sharing" becomes "Store files online, access them from all your
devices, and share them with coworkers". Same facts, verbs first, half the
hedging.

## Where the harness's standard goes further

Three things `meowctl`'s skill has that neither big-tech guide does, and all
three earn their place.

Every decision carries its reason. A rewrite that drops a "because", a
constraint or a motivation is wrong even when it is shorter. This is in direct
tension with "prune every excess word", and placement resolves it where
compromise would not. The reason goes where a reader deciding whether the rule
applies will look for it, and never into a how-to guide or a reference entry.

The same voice in chat. A reply to a reviewer is written to the same
standard as a document: a person answering a person, a reason for every choice,
a question at the end where there is one. Most style guides stop at published
artifacts, which leaves the highest-volume output ungoverned.

Living words. The skill cites Nora Gal's _Слово живое и мёртвое_ - the
Russian tradition's name for the same disease English calls nominalisation and
officialese: verbs turned into nouns, actors deleted, sentences that describe
processes nobody performs. It is the most precise available diagnosis of what
goes wrong in generated technical prose, and the cure is the same in both
languages: find the actor, use the verb.

## The document-type skeleton

Both guides and the harness agree that the type fixes the skeleton before a
word is written. The harness needs skeletons the guides do not cover, because
its document types are its own: the eight step artifacts and the decision
record. Deciding the reader level first - learning, integrating, evaluating -
and stating it at the top of a draft, as `meowctl`'s skill does, is what makes
review of the prose possible at all. A reviewer checks whether the text matches
the declared level.

## Checkability

This is the weakest part, honestly. Most of the standard is a judgement, and
the harness's own preference is for obligations a check can fail.

What _is_ checkable, mechanically:

- Hedges and filler, as a named list the check carries rather than this
  document, so that naming them here does not trip it.
- "There is/are/were" as sentence openers.
- Title case in headings.
- Passive constructions with no actor.
- Sentence length distribution, as a weak proxy for the list-of-laws rhythm.

What is not: whether a reason is present and load-bearing, whether the voice has
an author, whether the reader level matches the text. Those are review
questions, which is an argument for the documentation step preceding verification rather than for pretending a linter can settle them.

The honest position for the skill: state the mechanical checks as a gate, and
the judgements as review criteria, and do not dress the second group up as the
first.

## Conclusions

1. Loaded in every conversation, before anything is written, including for
   commit messages and chat replies.
2. The Google/Microsoft intersection as the baseline, with Microsoft's
   brevity rules as the editing pass.
3. Every decision carries its reason, placed where a reader judging
   applicability will look.
4. The contrasting sample, not a description of it - the skill teaches by
   showing the philosophy-treatise failure beside its fix.
5. Find the actor, use the verb.
6. Declare the reader level at the top of a draft.
7. Mechanical checks in the gate; judgements in review, and no confusion
   between the two.

## Sources

- [Google developer documentation style guide highlights](https://developers.google.com/style/highlights),
  read 2026-09-20 - second person, active voice, present tense, sentence case,
  serial comma, list forms, code font, writing for a global audience.
- [Microsoft Writing Style Guide: top 10 tips for style and voice](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice),
  read 2026-09-20 - bigger ideas fewer words, write like you speak, get to the
  point fast, be brief, sentence case, the serial comma, and "revise weak
  writing" with its before-and-after examples. Page dated 2026-07-02.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
  read 2026-09-20 - that prompt formatting influences output formatting.
- `~/workspace/meowctl/.claude/skills/technical-english/SKILL.md`, read
  2026-09-20 - the always-loaded policy, the contrasting target and avoid
  samples, the reader levels, the reason-carrying rule, and the citation of
  Nora Gal's _Слово живое и мёртвое_.
