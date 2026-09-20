---
id: RES-0202
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0005, RES-0201
---

# Progressive disclosure

## Summary

Six loading tiers exist where this project used to read three, and the two
above the skill are the expensive ones. An import defers nothing, so splitting
a long constitution into files saves no context; only path-scoped rules defer.
The first question asked of any instruction is whether a program could settle
it, because the platform states that instructions are context, which enforces
nothing. And shorter is better for correctness as well as for cost: across
eighteen models, reliability falls as input grows, a single distractor
measurably hurts, and coherent prose does no better than shuffled.

Research for the principle by which every instruction the harness ships is cut
into a constitution, a rule, a command, a skill, a reference file or a script.

It covers the loading tiers the platform actually has, and why a shorter
context is better for correctness as well as for cost. It also gives the
procedure for placing a given sentence, and the rules that constrain moving
something down a tier.

It does not cover what a skill costs, which is measured in
[RES-0005-skill-format.md](RES-0005-skill-format.md), nor the authoring surface,
which is [RES-0201-skill-authoring.md](RES-0201-skill-authoring.md).

## The question

A harness is instructions. A catalogue of two dozen plugins is a standing tax
on every session in every repository that installs it, and the tax is paid
whether or not the instruction is used.

Cutting the instruction correctly is therefore not tidiness. It is the
difference between a harness somebody installs and one whose cost is paid
continuously for a benefit taken rarely.

So: what are the tiers, what goes in each, and what must never move.

## Method

We fetched and read the platform's material on 2026-09-20. The engineering
account supplied the three named levels and the guidance on separating rarely
combined paths. The context-engineering account supplied the attention budget
and just-in-time retrieval, the memory documentation the tiers above the skill,
and the skills and plugin pages the limits.

The independent measurement of degradation with input length was fetched and
read for its sample, its task families and its headline conclusion, which we
quote in full.

Two secondary sources disagree about the per-skill metadata cost, and both are
recorded as reported, with neither chosen.

Nothing was measured here. No skill of this project's was profiled, which is
why the conclusion is that a measurement settles the cut, where an argument
settles nothing.

## Findings

### Progressive disclosure is the platform's own stated design principle

The vendor's description is explicit. Progressive disclosure is _"the core
design principle that makes Agent Skills flexible and scalable"_, working like
_"a well-organized manual that starts with a table of contents, then specific
chapters, and finally a detailed appendix."_

Three named levels. The metadata _"provides just enough information for Claude
to know when each skill should be used without loading all of it into
context"_. The body is _"the second level of detail"_ and loads when the skill
is judged relevant. And bundled files are _"the third level (and beyond) of
detail, which Claude can choose to navigate and discover only as needed."_

### There are more tiers than three, and the ones above the skill are the expensive ones

The three-level description is about skills. The harness also ships things that
load before any skill is considered, and those are where a mistake costs most.

| Tier | What it is                                 | When it loads                               | Who pays                          |
| ---- | ------------------------------------------ | ------------------------------------------- | --------------------------------- |
| 0    | `CLAUDE.md`, and `@path` imports from it   | Start of every session                      | Every session, always             |
| 0    | A rule in `.claude/rules/` with no `paths` | Start of every session                      | Every session, always             |
| 1    | A rule in `.claude/rules/` with `paths`    | When a matching file is opened              | Sessions touching those files     |
| 2    | A skill's `name` and `description`         | Start of every session, per installed skill | Every session, per skill          |
| 3    | A skill body                               | On invocation                               | The invoking session, once        |
| 4    | A bundled reference file                   | When the body sends the model to it         | Only the branch that needs it     |
| 5    | A script                                   | Executed, not read                          | Nothing, unless read as reference |

Two facts about tier 0 decide most of the harness's shape.

The size guidance is specific and the reason is not cost. The documentation
says to _"target under 200 lines per CLAUDE.md file"_ and states why: _"Longer
files consume more context and reduce adherence."_ Adherence, not tokens. A
long constitution is followed less well than a short one.

An import is not deferred loading. `@path` imports are _"expanded and
loaded into context at launch alongside the CLAUDE.md that references them"_,
recursively to a depth of four. Splitting a long constitution into imports
organises the files and moves nothing out of the context.

`.claude/rules/` is the mechanism that does move something. A rule without a
`paths` field loads at launch _"with the same priority as
`.claude/CLAUDE.md`"_, and a rule with one loads only when Claude works with
matching files. The documentation states the division this project should
follow directly:

> For task-specific instructions that don't need to be in context all the time,
> use skills instead, which only load when you invoke them or when Claude
> determines they're relevant to your prompt.

### Context is not enforcement, which decides what may be a rule at all

The documentation is blunt about what an instruction is:

> Claude treats them as context, not enforced configuration. To block an action
> regardless of what Claude decides, use a PreToolUse hook instead.

So a prohibition that must hold is not a paragraph. It is a hook, or a check in
the gate, or it is a thing the harness hopes for. Writing it more emphatically
does not change its category.

That is the most important consequence of this research for the harness. Every
instruction in tier 0 is examined for whether a check could carry it, because a
check enforces and an instruction is a suggestion with good manners.

### A shorter context is better for correctness as well as for cost

This is the half of the argument that makes the principle a design rule, and no
economy.

The vendor's position. Context is _"a finite resource with diminishing marginal
returns"_ and models have an _"attention budget"_. So _"as the number of tokens
in the context window increases, the model's ability to accurately recall
information from that context decreases"_, which follows from the quadratic
pairwise relationships a transformer maintains.

The independent measurement is stronger and more specific. Across 18 models -
including GPT-4.1, Claude 4, Gemini 2.5 and Qwen3 - over needle retrieval,
distractor, haystack-structure, conversational memory and text-replication
tasks, the headline finding is:

> models do not use their context uniformly; instead, their performance grows
> increasingly unreliable as input length grows

Three results from it bear directly on how instruction is cut.

Lower similarity degrades faster. _"Performance degrades more quickly in input
length with lower similarity needle-question pairs."_ An instruction phrased in
different words from the task it governs is harder to find as the context grows

- which argues for instructions written in the vocabulary of the work, where
  the method's own vocabulary is harder to find.

A single distractor hurts, and unevenly. _"Distractors have non-uniform
impact on model performance."_ Loading a skill that is nearly relevant is not
free; it is a distractor with a measured cost.

Coherence hurts. _"Models perform better on shuffled haystacks than on
logically structured ones."_ This is counter-intuitive, and it carries
carefully: it does not mean a document should be disordered. It means the
model's advantage does not come from the surrounding narrative, so prose that
exists to connect obligations is paying twice - once in tokens, once in
retrieval.

Together these say the same thing from three directions: **the goal is the
shortest relevant context, and never the most complete one.** The survey
reports roughly 40% fewer tokens with task completion 15-20% better for the
three-tier split. The accuracy gain is the surprising half, and these results
are why it stops being surprising.

### The compaction budget decides what survives, which is a different question from what loads

After auto-compaction the most recent invocation of each skill is re-attached,
keeping the first 5,000 tokens of each, with a combined budget of 25,000 across
all of them.

So a skill body has two regions with different properties: the first 5,000
tokens, which survive a long session, and the rest, which do not. That is the
mechanical reason the harness puts obligations and prohibitions first and
everything explanatory after - not a stylistic preference about topic
sentences.

### The decision procedure

Given a sentence of instruction, four questions place it, asked in order.

1. Can a program settle it? If yes it is not instruction at all. It is a
   check, a hook or a script, and writing it as prose creates a rule that is
   followed sometimes and reported never. This question is first because it
   removes the most material.

2. When is it needed?

   | Needed                              | Goes                       |
   | ----------------------------------- | -------------------------- |
   | Every session, whatever the work    | The constitution, tier 0   |
   | Whenever a matching file is touched | A path-scoped rule, tier 1 |
   | When a named activity happens       | A skill body, tier 3       |
   | Only in one branch of that activity | A reference file, tier 4   |

3. Is it an obligation or is it reference? An obligation constrains what the
   agent may do and belongs in a body; reference is data the agent consults - a
   table of commands, a template, a per-language idiom list, a taxonomy - and
   belongs in a file. The test is whether a reader who never opens the file would
   do the wrong thing: if yes, it is an obligation and may not be moved down.

4. Is the reading long and the conclusion short? Then the work is delegated
   to a forked context, so the reading never enters the main one. A review over a
   large diff and a search across a corpus are both this shape.

### What must not move down

Moving instruction down a tier is cheap and is the default temptation, so the
constraints matter more than the permissions.

An obligation may not live in a reference file, because a reference file is
read at the model's discretion and an obligation that is sometimes read is not
an obligation.

A prohibition belongs in the first 5,000 tokens of the body, because it fails
by being forgotten in a long session, and never by being disagreed with. This
project has a worked example: the ban on attribution is one sentence, is never
argued with, and is broken by a platform reminder arriving later in a session.

A description may not summarise the body. The description is charged every
session; the body is charged once when invoked. A description that explains
what the skill does pays permanently for something the invocation would supply
anyway. It answers one question: when should this be used.

A reference file the body never points at is unreachable. The third tier
works because the body names what to load and when; an unnamed file is a file
that is never read, which is worse than not writing it.

Mutually exclusive branches are separate files. The vendor's guidance is
exact: _"if certain contexts are mutually exclusive or rarely used together,
keeping the paths separate will reduce the token usage."_ A single reference
covering both branches is loaded whole for either.

### Code is a tier of its own, and the distinction has to be stated

Bundled code serves two purposes - _"as executable tools and as documentation"_

- and the guidance is to be _"clear whether Claude should run scripts directly
  or read them into context as reference"_, since execution is often more
  efficient than instruction-following.

For this harness the distinction is sharper than efficiency. A script that is
run produces a result which is evidence; a script that is read produces an
understanding which is not. The pack says which it is, and a script meant to be
run is never summarised in prose beside it, because the summary is the thing
that goes stale.

### Invocation decides the cut, and the file type decides nothing

A custom command is a skill. Whether a person invokes it, the model invokes it,
or both, is a frontmatter decision.

So the old question _should this be a command or a skill_ has no content. The
real questions are who may invoke it, when it loads, and what it costs while it
is not loaded. A command with side effects is a skill with
`disable-model-invocation`; a body of knowledge is a skill with
`user-invocable: false`; a language pack's knowledge is a skill with `paths`.

The plugin documentation confirms the direction, describing `commands/` as
_"Skills as flat Markdown files. Use `skills/` for new plugins"_.

### It is measurable, which settles this where an argument would not

`/skill-doctor` reports token cost per skill and how often each is invoked.
`claude plugin eval` runs a plugin against a set of prompts several times, with
it loaded and without. That measures what the plugin contributes, and it
catches a regression when the plugin changes or a new model ships.

Two figures in this document come from secondary sources and disagree with each
other: one reports roughly 80-100 tokens per installed skill's metadata,
another roughly 30-50. Both are recorded as reported, and the platform's own
measurement is what settles it for a given installation - which is the point of
having a measurement, where a published figure settles nothing.

## Conclusions

1. Instruction is cut by when it is needed, into six tiers: always loaded,
   path-scoped, description, body, reference file, script. 2. The first
   question asked of any instruction is whether a program could settle it,
   because context enforces nothing and a rule that must hold is a hook or a
   check, and never a paragraph. 3. The constitution stays under roughly 200
   lines, since the documented reason for the limit is adherence, and not cost. 4. An `@path` import does not defer anything, as imports are expanded at
   launch, so splitting a constitution into imports organises files and saves
   no context. 5. Instruction that applies only to certain files is a
   path-scoped rule, which is the only mechanism between always-loaded and
   invoked. 6. Task-specific instruction is a skill, and never a rule,
   following the platform's own stated division. 7. The goal is the shortest
   relevant context, and never the most complete one, because models do not use
   context uniformly and reliability falls as input length grows. 8. A nearly
   relevant skill loaded is a distractor with a measured cost, so loading
   something that might help is not free. 9. Connective prose is paid for twice
   - in tokens and in retrieval - since structural coherence does not help the
     model find what it needs. 10. Instructions are written in the vocabulary of
     the work, because retrieval degrades faster when the wording differs from
     the task. 11. Obligations and prohibitions occupy the first 5,000 tokens of
     a body, which is the region that survives compaction. 12. An obligation is
     never moved to a reference file, since a reference file is read at the
     model's discretion. 13. A description says when to use the skill and never
     what it contains, because it is the only part charged in every session. 14.
     A reference file the body does not name is unreachable and should not be
     written. 15. Mutually exclusive branches go in separate files, or both are
     loaded for either. 16. A long read with a short conclusion is delegated to a
     forked context. 17. A script states whether it is to be run or to be read,
     and one meant to be run is not summarised in prose beside it. 18. The
     command-against-skill question has no content: one artifact shape, with
     invocation, activation and cost set in frontmatter. 19. A measurement
     settles the cut, where an argument settles nothing, through the per-skill
     cost and invocation report and through evaluation with and without the
     plugin loaded. 20. Figures taken from secondary sources are recorded as
     reported, and where two disagree the measurement on the installation settles
     it.

## Sources

All read 2026-09-20.

- [Equipping agents for the real world with Agent
  Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
  - progressive disclosure as the core design principle, described as a manual
    with a table of contents, chapters and an appendix; the three levels of
    metadata, body and bundled files with what each is for; the guidance to move
    scenario-specific context into separate files and to keep mutually exclusive
    or rarely combined paths separate; and code as both executable tool and
    documentation, with the instruction to be clear which. - [Effective context
    engineering for AI
    agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  - context as a finite resource with diminishing marginal returns; the
    attention budget and the quadratic pairwise relationships behind it; that
    recall decreases as tokens increase; the right altitude between hardcoded
    logic and vague guidance; just-in-time retrieval through lightweight
    identifiers, where pre-loading pays for everything; and structuring a prompt
    into delineated sections. - [Context rot: how increasing input tokens impacts
    LLM performance](https://www.trychroma.com/research/context-rot) - 18 models
    including GPT-4.1, Claude 4, Gemini 2.5 and Qwen3; the five task families;
    that performance degrades faster with lower needle-question similarity; that
    distractors have non-uniform impact; that models perform better on shuffled
    haystacks than on logically structured ones; the repeated-words replication
    failures; and the conclusion that models do not use their context uniformly
    and grow unreliable as input length grows. - [How Claude remembers your
    project](https://code.claude.com/docs/en/memory) - `CLAUDE.md` loaded at the
    start of every session; the 200-line target with reduced adherence as the
    stated reason; `@path` imports expanded at launch to a depth of four hops;
    `.claude/rules/` loading at launch at the same priority without `paths` and
    only on matching files with it; the instruction to use skills for
    task-specific material; that instructions are context, which enforces nothing
    and that a `PreToolUse` hook is what blocks an action; that contradictory
    rules may be resolved arbitrarily; and that block-level HTML comments are
    stripped before injection. - [Skills](https://code.claude.com/docs/en/skills)
  - progressive disclosure with descriptions in context every turn and bodies
    on invocation; supporting files referenced from the body; the 1,536-character
    description cap; and the guidance to keep a body under 500 lines because
    content persists across turns. - [Create
    plugins](https://code.claude.com/docs/en/plugins) - `commands/` described as
    skills as flat files with `skills/` preferred for new plugins; plugin skills
    always namespaced; and `claude plugin eval` measuring what a plugin
    contributes across repeated prompts with and without it loaded. -
    [RES-0005-skill-format.md](RES-0005-skill-format.md) - the measured tier
    costs, the persistence of a loaded body across turns, the 5,000-token
    per-skill and 25,000-token combined compaction budget, and the reported 40%
    token reduction with 15-20% better task completion.
