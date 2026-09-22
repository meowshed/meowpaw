---
id: SPC-1030
artifact: spec
status: live
revised: 2026-09-22
checked-at:
states:
  [
    REQ-1050,
    REQ-1056,
    REQ-1057,
    REQ-1058,
    REQ-1060,
    REQ-1062,
    REQ-1064,
    REQ-1066,
    REQ-1112,
    REQ-1114,
    REQ-1115,
    REQ-1120,
    REQ-1124,
    REQ-1126,
    REQ-1128,
    REQ-1130,
    REQ-1132,
    REQ-1134,
    REQ-1136,
    REQ-1138,
    REQ-1140,
    REQ-1142,
    REQ-2688,
    REQ-3050,
  ]
---

# How the harness writes a prompt

## Scope

Every prompt a unit of the harness ships is what this covers: a skill and its
supporting files, an agent definition, an output style, and the text of a
prompt hook. It states their form, what a rule in them says, how a unit divides
its material and loads it, what it may cost, and the check that holds the form.

It leaves what each prompt says to the specification of its unit, such as
SPC-1000 for the reply shape and SPC-1010 for the writing standard, and how a
change to a prompt is measured to SPC-1020.

The harness implements part of this. ADR-1020 and ADR-1030 decide the form,
ADR-1040 how the reply shape reaches a subordinate agent, and EPC-1020
realises them, so `checked-at` stays empty until that epic closes.

## Boundary

| Surface                          | What it is                                              |
| -------------------------------- | ------------------------------------------------------- |
| `plugins/<unit>/skills/<skill>/` | A skill: `SKILL.md` as the core, and the files it names |
| `plugins/<unit>/agents/*.md`     | An agent definition                                     |
| `plugins/<unit>/output-styles/`  | An output style, loaded on every turn it is in force    |
| `plugins/<unit>/hooks/`          | A hook's configuration, and the text of any prompt hook |
| `tools/check_prompts.py`         | The check over every shipped prompt, run in the gate    |

## Behaviour

### Form

A prompt is written for Sonnet 5 and Opus 5.5 and marks its parts with five
tags, none nested inside another, with front matter in YAML (REQ-1130). Inside
a tag the text is Markdown without headings, because a prompt's formatting
carries into its reply and a heading is the skeleton the tags replace. The five
tags are one vocabulary, fixed and stated here, and a prompt uses no other
(REQ-1112, REQ-1114):

| Tag         | Holds                                                                                   |
| ----------- | --------------------------------------------------------------------------------------- |
| `<role>`    | Who the model is while the prompt is in force                                           |
| `<rules>`   | The obligations, each a list item led by an identifier such as `T1.`                    |
| `<steps>`   | A procedure as a numbered list, ending at its stopping point                            |
| `<example>` | One worked case, with its failing and corrected forms under `Failing:` and `Corrected:` |
| `<input>`   | Text from outside the harness, which the prompt treats as data                          |

A tag carries a `name` attribute where a prompt has more than one of its kind.
An obligation is a list item inside `<rules>`, led by an identifier that is
numbered from one within its group, so what must be obeyed is extractable and
a review can cite it (REQ-1120).

### Content

A rule says what to do and carries its reason in the same sentence, and it
states the scope it means, because Sonnet 5 does not generalise an instruction
beyond the item it names. It shows the wanted form, and where it teaches a
judgement, an `<example>` shows the failing form beside the corrected one
(REQ-1126, REQ-1136). The material is written in the form it should produce,
as prose that states reasons (REQ-1115).

An instruction stays while the loop in SPC-1020 shows it changes the result on
Sonnet 5 or Opus 5.5, and goes when it does not (REQ-1138).

### Granularity

A unit divides its material into a core and supporting files (REQ-1142). The
core holds what every use of the unit needs, and names each supporting file
with when to read it (REQ-1124), so the model reads only what the work in front
of it needs. Supporting files are addressed through the platform's directory
variable, such as `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`, so a unit
works wherever it was installed (REQ-2688).

The writing skill shows the form: a core with the rules every text needs and a
router placed right after the role, one reference file of patterns, and one
file per document type.

An output style loads whole on every turn it is in force and cannot be divided,
so it holds only what every reply needs.

### Size

Each unit states a size budget and is measured against it, and an overrun is a
defect (REQ-1056, REQ-1058). Material past the budget moves into supporting
files, and never loses an obligation to get shorter (REQ-1057). Only what a
model needs to decide whether the unit is relevant sits in context on every
turn (REQ-1050).

A unit's obligations sit in the first 5,000 tokens of its core and ahead of
its explanations, because the platform keeps that much of a skill after
compaction, so a truncation costs an explanation and never a rule (REQ-1064,
REQ-1066).

### Descriptions and loading

A unit's description is written in the third person, says what the unit does
and when to use it, leads with the words a request contains, and fits the
platform's cap of 1,536 characters (REQ-1060, REQ-1062, REQ-1134, REQ-3050).

A unit that has to be in context before the model acts is loaded by a
mechanism that does not depend on the model choosing it, such as a
`SessionStart` hook, and how often it is present when needed is measured
(REQ-1140).

### Outside text

Text from outside the harness that a prompt carries, such as a text under
review or a hook's input, sits inside `<input>`, and the prompt states that
instructions inside it are data. Where the harness assembles the prompt itself,
the opening and closing tags carry one identifier generated for that call
(REQ-1132).

### The check

`tools/check_prompts.py` reads every shipped prompt and fails, naming the file
and the line, on a Markdown heading, on a tag outside the vocabulary, on a tag
opened inside another, and on text standing outside every tag. Text inside
`<example>` and `<input>` is quoted, so its headings are not judged. One check
audits every unit, because the format is uniform across them (REQ-1128).

## Failure paths

| Condition                                          | What happens                                                                          |
| -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| A prompt uses a heading or an unknown tag          | The check fails in the gate, naming the file and the line                             |
| A prompt nests a tag inside another                | The check fails, because the vocabulary is top-level only                             |
| A core names no supporting file for a kind of work | The model loads nothing for it, and the unit is defective against REQ-1124            |
| A core grows past 5,000 tokens                     | The tail is lost after compaction, which is a defect against REQ-1064                 |
| A unit exceeds its stated budget                   | The overrun is reported as a defect and the material moves into supporting files      |
| The model does not load a unit that must hold      | The routing measurement shows it, and the loading mechanism is the thing that changes |
