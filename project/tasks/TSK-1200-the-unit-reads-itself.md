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

Not yet. The task closes on the reviewer's findings for each file, and beside
each finding the change that fixed it or the reason it was disputed.

## Left alone

`meow-core`'s material, which TSK-1190 rewrites to the standard and measures.
