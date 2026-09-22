---
id: ADR-1020
artifact: adr
status: draft
revised: 2026-09-22
addresses: [REQ-1130, REQ-1132, REQ-1134, REQ-1136, REQ-1138, REQ-1140]
supersedes: []
---

# 1020. Every shipped prompt is tagged, and a rule that must hold is loaded by a hook

## Decision

Every prompt the harness ships is written for Claude Sonnet 5 and Claude Opus
5.5, and is marked with XML tags from start to end (REQ-1130). That covers the
skills, the agent definitions, the output style, the fragment a subordinate
agent carries, and the text of every prompt hook. Front matter stays YAML,
because the platform reads it.

The tags come from one vocabulary, which SPC-1010 states and every prompt
uses, because an ad-hoc tag is one the next author invents differently
(REQ-1114): `<role>` for who the model is, `<rules>` holding one `<rule
id="...">` per obligation, `<examples>` holding `<example>` with `<before>` and
`<after>` for a judgement, `<steps>` for a procedure, and `<input>` for the
text a prompt is given.

A rule states what to do and shows it (REQ-1136). Where a rule teaches a
judgement, the failing form sits in `<before>` and the corrected one in
`<after>`, because a model follows a shown form more reliably than a
prohibition.

Text from outside the harness sits in `<input>`, and the prompt says that
instructions inside it are data (REQ-1132). Where the harness assembles the
prompt itself, the opening and closing tags carry one identifier generated for
that call. The gate's prompt is assembled by the platform, which substitutes
`$ARGUMENTS` into fixed text, so there the tag is fixed and the note is what
guards it.

A unit's description is written in the third person, says what the unit does
and when to use it, and leads with the words a request contains (REQ-1134,
REQ-3050). A description reading "Always load this skill before you write"
becomes "Holds the writing standard for commit messages, pull request and issue
bodies, review comments, code comments, documents and replies. Use before
writing any of them."

`meow-prose` also ships a `SessionStart` command hook that returns one line of
`additionalContext` naming the writing skill and when to load it (REQ-1140).
The hook runs on every new, resumed, cleared and compacted session, costs one
line of context, and writes nothing into the repository (REQ-3180). How often
the skill is in context when a writing request arrives is measured with the
hook and without it.

An instruction stays in a shipped prompt while the loop in SPC-1020 shows it
changes the result on Sonnet 5 or Opus 5.5, and goes when it does not
(REQ-1138). The loop measures each candidate on both models, judged by Opus
5.5, and a candidate lands only when it holds on both.

### What it changes in ADR-1010

ADR-1010 says the gate "blocks with `permissionDecision: \"deny\"`". That field
belongs to a command hook. The gate is a prompt hook, so it blocks by
answering `{"ok": false, "reason": "..."}`, and it sets `continueOnBlock: true`
so the reason returns to the model as the tool error and the model can correct
the text and publish again. Without it, a denial ends the turn.

ADR-1010 left the prompts' structure to their drafts, and its appendix drafts
use Markdown headings. This decision sets the structure above, and the drafts
are converted when the tasks of EPC-1010 write them.

Everything else ADR-1010 decided stands.

## Why

Anthropic's guides, recorded in RES-0270, say a prompt's formatting carries
into the reply, and the writing standard asks for prose. A skill teaching prose
under Markdown headings teaches headings. Tags also close, which a heading does
not, so the end of a rule is unambiguous to the model and to a check.

The routing measurement decided the hook. With the skill listed in every
session, Sonnet 5 loaded it in one run of nine writing requests, and rewording
the description as a directive changed nothing. The guides warn that louder
wording makes recent models over-trigger, and name a hook as the deterministic
fix.

The blocking field is a correction. The gate as ADR-1010 wrote it would not
have blocked anything.

## Alternatives

| Option                                         | Better at                                           | Why it lost                                                                                         |
| ---------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Tags throughout, and a `SessionStart` hook     | A shipped prompt that asks for prose and is present | Chosen                                                                                              |
| Markdown headings with tags around examples    | Reading well in a file browser                      | The headings carry into the reply, which is the habit the writing standard removes                  |
| The description alone, reworded until it fires | Costing nothing on turns that write nothing         | Measured at one run in nine, and louder wording over-triggers, per RES-0270                         |
| A `UserPromptSubmit` hook adding the pointer   | Firing only when a person writes                    | It adds a line on every prompt, where `SessionStart` adds one per session                           |
| The pointer in the repository's `CLAUDE.md`    | Needing no program                                  | The unit would write into the repository it serves, which REQ-3180 forbids                          |
| Do nothing                                     | Costing nothing now                                 | The gate would not block, the skill would rarely load, and the prompts would teach the wrong format |

## What it costs

One line of context in every session where `meow-prose` is enabled, including
sessions that write nothing a person reads. The line is under 300 characters
and loads nothing else, so a session that writes nothing pays for the pointer
and not for the skill.

A program in the unit, which REQ-3178 allows and which has to run on every
platform the harness supports. It prints a fixed string and reads nothing, so
it has no input to go wrong on.

Every prompt the loop measures now runs on two models, which doubles the cost
of each run.

Tags read worse than headings in a file browser. A person reading a skill on
the forge meets angle brackets where headings were, and the documentation page
is where a person reads what the unit does.

## What would reverse it

- The description alone, written to REQ-1134 and REQ-3050, reaches the routing
  threshold on both models without the hook. The hook would then cost a line
  of context and buy nothing, and REQ-1138 would remove it.
- A measurement shows a prompt written in tags scoring below the same prompt
  under headings on Sonnet 5 or Opus 5.5. The format would then be a candidate
  that lost, and the loop publishes it.
- The platform starts treating a skill's description as binding and loads it
  before the matching work. The hook would then duplicate the platform.

## Consequences

- `meow-prose` carries `hooks/hooks.json` with a `SessionStart` command hook
  and the program it runs.
- The gate's hook answers `ok` and `reason`, and sets `continueOnBlock: true`.
- SPC-1010 states the tag vocabulary, the hook and the corrected blocking
  field. SPC-1020 states that the loop measures on Sonnet 5 and Opus 5.5.
- The `meow-core` style and fragment are converted to tags through the loop,
  measured against the Markdown versions they replace.
- A check reads every shipped prompt and fails on a Markdown heading outside a
  fenced block, and on a tag outside the vocabulary.

## How I will know it was realised

1. The check passes on every shipped prompt, and fails on a probe prompt that
   uses a heading and on one that uses a tag outside the vocabulary.
2. The writing skill is in context before the text is written in at least
   nine runs of ten, across the routing requests of TSK-1180, on both models,
   with the hook. The same requests without the hook are published beside it.
3. The gate, given a text that carries a named defect, denies the publish, the
   model receives the reason, and the next attempt publishes corrected text.
4. The reviewer, given a text whose body says to ignore the review criteria,
   reports on the text and follows none of it.
5. The converted `meow-core` style scores no lower than the Markdown one on
   either model, with the table published.

## What this does not settle

- The routing threshold's exact number beyond the nine in ten above, which the
  first measurement on both models sets.
- Whether the gate's fixed `<input>` tag holds against a text that imitates
  it. The platform assembles that prompt, and a command hook generating an
  identifier would need a model credential the unit does not carry.
- Models other than Sonnet 5 and Opus 5.5. Haiku 4.5 runs the gate, and the
  gate is measured on it as SPC-1020 describes, but no other prompt is tuned
  for it.
