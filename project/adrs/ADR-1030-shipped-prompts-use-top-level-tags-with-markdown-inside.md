---
id: ADR-1030
artifact: adr
status: draft
revised: 2026-09-22
addresses: [REQ-1130]
supersedes: []
---

# 1030. Shipped prompts use top-level tags with Markdown inside

## Decision

A prompt the harness ships marks its parts with five tags, none nested inside
another: `<role>`, `<rules>`, `<steps>`, `<example>` and `<input>`. Inside a tag
the text is Markdown: a list, a numbered list, code spans and fences. A tag
carries a `name` attribute where a prompt has more than one of its kind.

Each rule is a list item inside a `<rules>` block, led by an identifier a
review can cite, such as `T1.` or `D4.`. Each example is its own `<example>`,
with its failing and corrected forms under the plain labels `Failing:` and
`Corrected:`. Text from outside the harness still sits in `<input>` (REQ-1132).

Markdown headings stay out, inside a tag and outside one (REQ-1130), because a
heading is the skeleton the tags replace.

### What it changes in ADR-1020

ADR-1020 nested `<rule id="...">` inside `<rules>`, and `<before>` and
`<after>` inside `<example>`, under an `<examples>` wrapper. Those four tags
leave the vocabulary. Everything else ADR-1020 decided stands: tags throughout,
one vocabulary, a hook that loads the writing skill, and the gate's blocking
field.

## Why

The owner decided it on 2026-09-22, while the writing skill was being split
into a core and one file per document type.

A closing tag on every rule costs tokens the rule does not need. Converting the
writing skill's core from nested tags to this form took it from 5,322 tokens to
4,904 on Sonnet 5, with the same rules, which brings it back under the 5,000
REQ-1064 allows. The pattern reference went from 2,868 to 2,753.

The top-level tags still give each part a boundary that closes, which is what
REQ-1130 asks of them, and an identifier at the head of each list item keeps a
rule extractable (REQ-1120).

## Alternatives

| Option                              | Better at                                         | Why it lost                                                                              |
| ----------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Top-level tags with Markdown inside | Fewer tokens, and text a person edits as Markdown | Chosen                                                                                   |
| Nested tags, as ADR-1020 decided    | A boundary around every single rule               | A closing tag per rule costs about 8% of the core, and nothing measured it as worth that |
| Markdown only, headings included    | Reading well on the forge                         | REQ-1130 forbids headings as a prompt's skeleton, because they carry into the reply      |
| Do nothing                          | Costing nothing now                               | The writing skill's core stays over the 5,000 tokens REQ-1064 allows                     |

## What it costs

Lists inside a prompt may carry into replies the way headings do, which is the
risk ADR-1020 took tags to avoid. The loop in SPC-1020 measures it: a rise in
list-shaped replies on the cases that ask for prose is the signal.

`tools/check_prompts.py`, which TSK-1230 writes, changes with the vocabulary:
it fails on a nested tag as well as on a heading and an unknown tag.

## What would reverse it

A measurement showing the Markdown-inside form scoring below the nested form on
Sonnet 5 or Opus 5.5, on the same cases, would restore the nested vocabulary.

## Consequences

This decision adds no task. The tasks that write each prompt realise it: TSK-1110
and TSK-1120 for the writing skill and the reviewer, TSK-1140 for the gate, and
TSK-1230 for the check and the `meow-core` style and fragment.

- SPC-1010 states the five-tag vocabulary and the rule form.
- The writing skill, the reviewer, the gate's prompt, the `meow-core` style and
  its fragment are written in this form.
- The check reads a rule as a list item inside `<rules>`, and the style check
  reads each list item as a rule that has to state when it yields.

## How I will know it was realised

1. `tools/check_prompts.py` passes on every shipped prompt, and fails on probes
   with a nested tag, a heading, and a tag outside the five.
2. The loop's table shows this form against the nested one on both models.

## What this does not settle

Whether lists inside a prompt raise lists in replies. The loop answers that,
and ADR-1030 reverses if it does.
