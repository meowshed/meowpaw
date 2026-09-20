---
id: RES-0005
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# What a skill costs, and what makes one work

## Summary

A harness is documents loaded into a context window, so the format is not a
matter of taste. The platform charges in three tiers: a description in every
session, a body on invocation, and supporting files on demand. Compaction
re-attaches only the first 5,000 tokens of each skill, against a combined
budget of 25,000. The measured three-tier split costs about 40% fewer tokens
and completes tasks 15-20% better, so brevity and effectiveness are not
opposed.

A harness is documents that get loaded into a context window. A catalogue of
two dozen plugins is a standing tax on every session in every repository that
installs them, so the format is no matter of taste. This records what the
platform actually charges, what the evidence says about effectiveness, and what
follows for the harness.

Sources: the [skills documentation](https://code.claude.com/docs/en/skills),
the [prompt engineering guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
and the measurements collected in
[Agent Skills: progressive disclosure as a system design pattern](https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure).

## Method

We read three sources on 2026-09-20. The platform's skills documentation gave
the tier behaviour, the truncation limits, the compaction budget and the size
guidance. The prompting guidance gave the structure advice, and one published
article gave the measurements.

The measurements are secondary. The 40% token reduction and the 15-20%
completion figures were not reproduced here, and are recorded as reported.

No measurement was taken on this project's own material, because there was none
to measure at the time. The conclusion that measurement belongs in the
harness's own gate follows from that absence, and from no result.

The session's tool record survives and was consulted for this section. It
confirms the three sources were fetched directly and that nothing was run.

## What is charged, and when

Three tiers, and they cost very differently.

| Tier       | What loads                                     | When                                       | Cost                                                               |
| ---------- | ---------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
| Discovery  | `name` and `description` from the front matter | Every session, every skill installed       | ~80-100 tokens per skill                                           |
| Body       | The whole of `SKILL.md`                        | When the skill is invoked                  | ~275 to ~8,000 tokens, median ~2,000 across Anthropic's own skills |
| Supporting | `reference.md`, `examples.md`, scripts         | Only when the body sends the model to them | Paid only if read; a script is executed, never loaded              |

Four platform behaviours follow from this and constrain the design.

The description is charged in every session whether or not the skill is
used. It is truncated at 1,536 characters combined with `when_to_use`. The
descriptions of whatever is installed are the harness's permanent floor, and
the only part a repository cannot avoid paying for.

A loaded body persists across turns. Claude Code does not re-read the file each
turn, and re-invoking a skill whose content is unchanged adds a note, and no
second copy. So the body is charged once per session, and never once per use -
which makes a long body cheaper than it looks, and a body that is loaded
needlessly more expensive than it looks.

Auto-compaction has a budget. After a summary, the most recent invocation
of each skill is re-attached, keeping the first 5,000 tokens of each, with a
combined budget of 25,000 tokens across all of them. Two consequences: the
first 5,000 tokens of a skill are the part that survives a long session, and
more than a handful of large skills loaded at once means some are dropped.

The platform can measure this. `/skill-doctor` reports token cost per skill and
how often each is invoked. That turns "does this skill earn its cost" into a
question a measurement answers, where an argument would not, and it is the
check the harness should use on itself.

## What the evidence says about the format

Progressive disclosure saves about 40%. Skills using the three-tier split are
measured at roughly 40% fewer tokens than the same content as one prompt, with
task completion 15-20% better. The accuracy gain is the surprising half and the
more important one: a shorter relevant context beats a longer complete one.

Anthropic's own guidance is to keep `SKILL.md` under 500 lines and move detail
into supporting files. It also says to keep the body terse, because every line
is a recurring cost once loaded: state what to do, narrating neither how nor
why.

XML tags earn their tokens where content is mixed. The guidance is that tags
disambiguate a prompt mixing instructions, context, examples and input, that
tag names should be consistent across prompts, and that nesting should follow
natural hierarchy. The cost is real but small - a tag pair is two to four
tokens - and it is paid once per section, and never per line.

But tags are not free and not always earned. A document that is one instruction
after another gains nothing from wrapping each in a tag; it gains from being
shorter. The tags pay where a reader, human or model, has to tell one kind of
content from another. That is exactly the case for a skill mixing obligations
with worked examples and failure cases.

Style propagates. The formatting of a prompt influences the formatting of
what the model produces. A skill written as terse bullets produces terse
bullets; a skill whose prose states reasons produces work that states reasons.
This is the tension the harness has to resolve: the standard wants rules to carry
their reasons, and token economy wants fewer words. They are only reconcilable
by moving the reasoning somewhere that is loaded when it is needed.

## The tension, stated plainly

Two of this harness's own findings pull against each other.

`meowctl`'s writing skill is 600-plus lines and is loaded in every
conversation by policy. It is the most effective internal artifact and the most
expensive one. Its effectiveness comes from exactly what makes it expensive:
worked contrasting samples, the reason behind each rule, a catalogue of
patterns to edit out.

A rule without its reason gets applied literally to a case its author did not
foresee. A reason costs tokens. Both are true.

The resolution is not to choose but to place them in different tiers:

- The **obligation** goes in the body, stated once, in the fewest words that
  are still unambiguous.
- The **reason** goes next to it only where the rule is counter-intuitive or
  where the model's default behaviour is the wrong one. Everywhere else it
  goes in a supporting file.
- The **worked examples**, the contrasting samples and the catalogue of
  patterns go in supporting files, referenced by name from the body.

A test settles this, and no taste is involved: `/skill-doctor` reports the
cost, and a plugin's eval suite reports whether behaviour changed when the
reasoning moved out of the body.

## Conclusions

1. A per-skill body budget, and a rule that anything longer moves to supporting
   files. 2. Descriptions written to a fixed budget, since they are the
   permanent floor. 3. The first 5,000 tokens of a body carrying the
   obligations, because that is what survives compaction. 4. One skill per
   discipline, and never several overlapping ones, so that invoking a
   discipline loads one body and not four. 5. Plugins split so that a
   repository pays discovery cost only for the disciplines it installed - which
   is the token argument for the plugin split, independent of the adoption
   argument. 6. Measurement as part of the harness's own gate, and never as a
   one-off audit.

## Sources

- [Agent Skills](https://code.claude.com/docs/en/skills), read 2026-09-20 -
  the three loading tiers, the 1,536-character description truncation, body
  persistence across turns, the compaction budget (first 5,000 tokens per
  skill, 25,000 combined), the 500-line guidance, and `/skill-doctor`.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
  read 2026-09-20 - XML tags for mixed content, consistent tag names, nesting by
  natural hierarchy, style propagation, and its warning that over-verification
  instructions carried from older prompt styles cost tokens on current models.
- [Agent Skills: progressive disclosure as a system design pattern](https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure),
  read 2026-09-20 - the measured ~40% token reduction and 15-20% task-completion
  improvement, and the body-size distribution across Anthropic's own skills
  (~275 to ~8,000 tokens, median ~2,000).
- `~/workspace/meowctl/.claude/skills/technical-english/SKILL.md` and
  `~/workspace/meowary/.claude/skills/context-gathering/SKILL.md`, read
  2026-09-20 - the two internal artifacts whose house tag vocabulary this
  section generalises from.
- `~/workspace/vlie/.claude/commands/work.md`, read 2026-09-20 - the compact
  command form that separates procedure from judgement in practice.
