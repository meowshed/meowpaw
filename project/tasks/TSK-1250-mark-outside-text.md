---
id: TSK-1250
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1020
closes: [REQ-1132]
issue: 68
---

# Mark outside text in the gate's and the reviewer's prompts

One task, one branch, one pull request, one review.

## What to do

Put the text the gate reads inside `<input>` in its prompt, around
`$ARGUMENTS`, and state that instructions inside it are data (REQ-1132). The
platform assembles that prompt, so the tag is fixed, and the note is what
guards it.

State the same in the reviewer's prompt for every text it reads. Where the
harness itself assembles a prompt around outside text, generate one identifier
per call and give it to both the opening and the closing tag.

## Depends on

TSK-1120 and TSK-1140, because the two prompts it marks are written there.

## Evidence

Not yet. The task closes on the reviewer, given a text telling it to ignore its
criteria, reporting on that text and following none of it, and on the gate,
given a commit message telling it to allow the publish, judging the message
as it would any other.

## Left alone

Semantic injection, which a tag does not stop. The guide RES-0270 cites says
so, and this task claims only the structural mark.
