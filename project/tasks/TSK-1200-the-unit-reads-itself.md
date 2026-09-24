---
id: TSK-1200
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-1115, REQ-1674, REQ-1676]
issue: 57
---

# Hold the unit's own material to its standard

One task, one branch, one pull request, one review.

## What to do

Run the reviewer over the unit's own material: the skill, the reviewer's own
prompt, the gate's prompt and the documentation pages of both units (REQ-1674,
REQ-1676). Somebody deciding whether to trust the rest of the harness reads
that material most closely.

Fix each finding or dispute it on the record. A disputed finding that is a
preference is a defect in the reviewer's prompt, and the prompt changes, not
the text it flagged.

Check that the loadable material is written in the form it should produce
(REQ-1115). Prose that states reasons produces work that states reasons, and a
list of terse bullets produces terse work.

## Depends on

TSK-1120, because the reviewer is what reads the material. TSK-1110 and
TSK-1140 land the texts it reads.

## Evidence

The reviewer as #99 landed it read each of the unit's seven texts in its own
`claude -p` session on Sonnet 5, told that rules quoted as examples and
failing examples shown on purpose are material. It found three defects at fix
level, all in `documents.md`, and about fifty at improve or note level. Every
one is fixed below except the three disputed at the end.

| Text                      | Findings                 | What changed                                                                                                                                                                    |
| ------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SKILL.md`                | 8 improve, 2 note        | G2 and X1 split; the serial commas F6 now forbids removed; check 2 searches "there are" in place of citing D5; "unit" became "plugin"; step 5 active; contractions where spoken |
| `documents.md`            | 3 fix, 6 improve, 4 note | E5, E9, E11 and E14 give their reasons; E2 and E7 rewritten; no idiom left; E10 allows the one pointer E9 needs; E6 opens with the answer; F4 exempts the elements F3 bolds     |
| `patterns/en.md`          | 6 improve, 1 note        | The role says what the file is and names its patterns as they are named; three idioms and one "instead of" rewritten, in `ru.md` too                                            |
| `agents/prose.md`         | 8 improve, 2 note        | Three long sentences split; scope names its steps; "it" given its noun; V5 says "leave alone"; V6 states its exception; the example's failing half is a vague finding           |
| the gate's prompt         | 4 improve                | "Ignore paths" limited to the published text, which contradicted the rule on hidden files; the bold-heading rule gives its reason; "hook" and "names" replaced                  |
| `docs/meow-prose.md`      | 7 improve, 2 note        | Install first; the skill and the reviewer introduced before they are used; the repeated report merged; the measurement cited; every count named as Sonnet 5's                   |
| `docs/meow-prose-gate.md` | 7 improve, 3 note        | One term per thing; Haiku 4.5 named at first use; the measurement and the idiom list cited; "very long" given its limit; the kernel named                                       |

The gate's prompt changed, so it was measured again with `tools/measure_gate.py`,
five runs of each of its twelve cases: 20 of 30 defects blocked and 30 of 30
clean texts passed, the same as the prompt #93 landed.

Disputed, with the reason:

- F1 and F4 missing from the skill's format group. They live in
  `documents.md`, and each rule keeps its identifier wherever it lives so that
  a review citing F4 still finds it.
- "heredoc" on the gate's page. It is the term its readers type, and a gloss
  would explain a word to the people who use it.
- C1's "about 30" against check 4's "over 35". C1 is the target and check 4 is
  the count that forces a split, so the gap is deliberate.

The loadable material is written as it should produce (REQ-1115): every rule
states its reason in prose. The skill's and the reviewer's wording changed
without changing what they ask for, and the next run of the loop in TSK-1260
measures them as they now stand. REQ-1115, REQ-1674 and REQ-1676 are closed.

## Left alone

`meow-core`'s material, which TSK-1190 rewrites to the standard and measures.
