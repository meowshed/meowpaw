---
id: RES-0272
artifact: research
status: approved
revised: 2026-09-23
elaborates: RES-0270, RES-0266
---

# Routing a skill by its description

## Summary

On Sonnet 5, a description that states an obligation loads the writing skill
where one that describes the skill does not. The description `meow-prose`
shipped loaded the skill in 0 of 30 writing runs. The best candidate loaded it
in 36 of 36, and in 0 of 39 near misses. That candidate opens with a sentence
saying what the skill is, and states in the third person that it MUST be
loaded. It names the verbs a request uses for the work, and it closes by saying the skill MUST NOT be skipped however
short the text looks.

A `SessionStart` hook naming the skill did not change behaviour, which removes
the reason RES-0270 gave for one. Opus 5.5 already loaded the shipped
description in 45 of 50 writing runs, so the failure was Sonnet 5's. On Opus
5.5 the new description loaded in 33 of 33 writing runs, and also on 8 of 39
near misses: answers in chat and a one-word fix to a README.

This record elaborates
[RES-0270-prompting-sonnet-5-and-opus-5-5.md](RES-0270-prompting-sonnet-5-and-opus-5-5.md),
whose sixth conclusion it contradicts, and uses the method of
[RES-0266-measuring-the-harness.md](RES-0266-measuring-the-harness.md).

## The question

ADR-1020 decided to load the writing skill with a `SessionStart` hook, because
Sonnet 5 loaded it in one run of nine and a directive description changed
nothing. RES-0270 read the guides' warning that aggressive wording makes recent
models over-trigger, and did not measure it. Two questions followed. Does the
hook load the skill? And is there a description that loads it on writing
requests and leaves it alone everywhere else?

## Method

I ran the measurement between 2026-09-22 and 2026-09-23 in a scratch
repository holding `worker.py`, a README and one staged change. Each run was a
fresh `claude -p` session with only the candidate's copy of `meow-prose`
installed through `--plugin-dir`, `--max-turns 8` and `acceptEdits`. A run
counted as a load when the transcript showed a `Skill` call naming
`meow-prose:writing`. The skill's body was the same in every candidate, and
only the front matter changed.

The requests were 11 that should load the skill and 13 near misses that should
not:

- The 11 writing requests: a README, a design proposal, release notes,
  documenting a file, a pull request description, rewording a sentence, an
  issue, a wiki explanation, a reply to a reviewer, a commit message, and
  reviewing a paragraph.
- The 13 near misses: renaming a variable, adding a test, fixing a bug,
  showing the log, counting lines, committing with a given message, changing a
  delay, listing functions as JSON, fixing a one-word typo, listing imports,
  and three answers in chat.

Most candidates ran each request three times. A result was stored under the
model, a hash of the front matter, a hash of the request and the run's index,
so an unchanged pair was never run twice. Every wrong result kept its
transcript. I compared candidates with Fisher's exact test, two-sided.

Two limits apply. At three runs a request, one candidate measured 29 of 33 in
one pass and 17 of 22 in the next two, so differences of about ten points are
noise. The wiki request first asked for a reason it did not supply, and the
model refused to invent one. That request was rewritten to supply the reason,
and the tallies below count only the rewritten one, so most candidates show 30
writing runs.

## Findings

### The shipped description loads on Opus 5.5 and not on Sonnet 5

The description `meow-prose` shipped read "Writing standard for commit
messages, pull request and issue bodies, ... Use before writing or editing any
text a person will read". It loaded the skill in 0 of 30 writing runs on
Sonnet 5, and in 45 of 50 on Opus 5.5 (p < 0.001). Neither model loaded it on
a near miss. The routing problem is Sonnet 5's, which reads a description
literally, as RES-0270 recorded from the Sonnet 5 guide.

### Opus 5.5 reads the obligation more widely

The best candidate, Z4, loaded the skill in 33 of 33 writing runs on Opus 5.5.
It stayed unloaded on every near miss that changes code, 0 of 30, and loaded on
three that produce prose: a summary of the last five commits in 3 of 3, a
two-sentence explanation of a file in 2 of 3, and a one-word typo fix in a
README in 3 of 3. Z4 names Markdown files and prose of any length, so Opus 5.5
followed its words where Sonnet 5 did not.

### A hook naming the skill does not load it

A `SessionStart` command hook printed one line naming the skill and the texts
it governs. The platform delivered the line as context, and Sonnet 5 still
wrote without loading the skill, in 1 run and then in 3 runs of a variant
naming the tool to call. The hook's line is advice at the start of a session,
and the model weighs it the way it weighs the description.

### An obligation in the third person loads the skill

| Candidate | Description, in short                                        | Writing | Near miss |
| --------- | ------------------------------------------------------------ | ------- | --------- |
| A         | Shipped: "Writing standard for ... Use before writing"       | 0/30    | 0/30      |
| E         | "Make sure to use this skill whenever ..."                   | 15/30   | 0/30      |
| I         | "It MUST be loaded BEFORE ...", long, with example requests  | 25/30   | 0/30      |
| N         | "It MUST be loaded before writing, editing or reviewing ..." | 48/50   | 1/50      |
| P         | N, naming pull request and issue descriptions                | 45/53   | 0/59      |
| S         | P as "You MUST load it to write ..."                         | 11/30   | 0/30      |
| T         | P as "You MUST use this skill to write ..."                  | 13/30   | 0/30      |
| Z4        | "The writing standard for all text. It MUST be loaded ..."   | 36/36   | 0/39      |

Stating an obligation moved the skill from never loaded to loaded: A against
E, 0 of 30 against 15 of 30 (p < 0.001). The same obligation addressed to the
model in the second person, S and T together, loaded in 24 of 60 runs against
45 of 53 for P in the third person (p < 0.001). The guides say a description is
injected into the system prompt and has to be in the third person, and this is
that rule measured.

The guides' warning that such wording over-triggers did not hold. Every
candidate after A was worded as an obligation, and across them the near misses loaded the
skill once, when N was asked to fix a one-word typo in a README. That is 1 of
882 near-miss runs on Sonnet 5.

### The opening sentence says what the skill is

Candidate X was P without its opening sentence, "Writing standard for every
text a person reads", and started at "MUST be loaded". It loaded in 14 of 30
runs against P's 45 of 53 (p < 0.001). The model reads the opening sentence as
what the skill is, and the obligation after it as when to load it. With the
first sentence gone, the obligation has nothing to attach to.

### Naming the verbs of a request loads the skill for that request

Sonnet 5 matched the verbs literally. P said "writing, editing or reviewing",
and loaded on the rewording request in 1 of 5 runs. Z4 added "rewritten" and
"reworded", and loaded on it in 6 of 6.

A word that names more than the skill covers cost loads. R added "replies" to
Q and loaded in 8 of 20 against 22 of 31 (p = 0.04), and O, "any text" in place
of "any prose", loaded in 20 of 30. A list of kinds does not stand in for the
verbs: J listed eleven kinds of text and loaded in 17 of 30, against 25 of 30
for I, which also named the verbs of a request (p = 0.05).

### Saying it holds however short the text is closes the gap

Z stated the obligation in plain grammar and loaded in 21 of 30, missing the
commit request every time. Z2 added one sentence, "It MUST NOT be skipped,
however short or simple the text looks", and loaded in 31 of 33 (p = 0.02). The
sentence answers the judgement the model makes on a short text, that it is too
small to need a standard. Naming the kind does not answer it: Z already named
commit messages.

### What did not change the result

These changes made no difference that the runs could tell apart from noise:

- Negatives and exceptions. H added "Do NOT use for changing code, writing
  tests ..." to G, and loaded in 9 of 30 against 15 of 30 (p = 0.19), with no
  near miss loading in either.
- A reason for loading. W-b added "because it holds the repository's prose
  language, templates and checks", to Q, and loaded in 21 of 30 against Q's 22
  of 31.
- The output style. P loaded in 27 of 30 with `meow-core:meow` active and in
  45 of 53 without it (p = 0.74).

A long description written as a catalogue of what the skill holds loaded in 10
of 30 (U) and 11 of 30 (V).

## Not measured

- Whether Z4 holds in a session that already has other work in its context.
  Every run here started clean.
- What the skill's body does once loaded. The body was held fixed so that only
  routing varied.

## Conclusions

1. A unit that has to be in context before the model acts is loaded by its
   description on Sonnet 5, when the description states the obligation. A
   `SessionStart` hook naming the unit did not change behaviour, so the reason
   RES-0270 gave in its sixth conclusion does not hold.
2. The obligation is stated in the third person with MUST, as in "It MUST be
   loaded before ...". The second person loads the unit in half as many runs.
3. The description opens with a sentence saying what the unit is, and states
   the obligation after it.
4. The description names the verbs a request uses for the work, such as
   written, rewritten, reworded, edited and reviewed, and names no kind of
   work the unit does not cover.
5. The description closes by saying the unit MUST NOT be skipped however short
   or simple the work looks.
6. On Sonnet 5, stating an obligation did not make the skill load on work it
   does not govern, measured on 13 near misses including answers in chat. The
   guides' warning about over-triggering is a claim to measure, not a reason
   to avoid the form.
7. Routing is measured on each model the unit serves, with near misses beside
   the requests that should load it, because Opus 5.5 and Sonnet 5 differed by
   45 of 50 against 0 of 30 on one description.
8. On Opus 5.5 an obligation over "any prose" loads the unit on answers in
   chat and on edits to a Markdown file. Whether that is a miss depends on
   whether the unit governs replies, and the decision that ships the
   description has to say which.

## Sources

- [Skill authoring best
  practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
  read 2026-09-22 - the description is injected into the system prompt and is
  written in the third person, and states what the skill does and when to use
  it.
- [Prompting best
  practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
  read 2026-09-22 - the warning that aggressive wording makes recent models
  over-trigger tools and skills, which the obligation finding measured.
- [Prompting Claude Sonnet
  5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5),
  read 2026-09-22 - literal instruction following, which the first finding and the
  verbs finding bear out.
- [Extend Claude with skills](https://code.claude.com/docs/en/skills), read
  2026-09-22 - the listing and its 1,536-character cap; the hook named as the
  fix for a skill that stops influencing behaviour, which the hook finding did not
  bear out.
- [Hooks reference](https://code.claude.com/docs/en/hooks), read 2026-09-22 -
  `SessionStart` output delivered as context, which the hook run confirmed.
- The measurement itself, run 2026-09-22 to 2026-09-23 on `claude-sonnet-5`
  and `claude-opus-5-5` by the method above - every table and count in the
  findings.
