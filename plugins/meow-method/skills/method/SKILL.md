---
name: method
description: The method's nine steps, research, requirements, design, spec, epic, implement, document, verify and review, and the gate each checks. It MUST be loaded before any research, requirement, decision, specification, epic or task record is written, before a task is implemented, and before an epic is documented, verified or reviewed. It MUST NOT be skipped, however small the record looks.
---

<role>
You run one step of the method at a time. Each step writes one artifact from
an approved input, because an artifact built on an unapproved one inherits a
decision nobody made. A program settles whether the input is ready, and you
don't overrule it.
</role>

<steps name="run a step">
1. Name the step and the identifiers of its input. The steps, in order, are
   research, requirements, design, spec, epic, implement, document, verify
   and review.
2. Read the repository's principles before producing anything: `CLAUDE.md`,
   and each file `.meowpaw/profile.toml` names under `[method] principles`.
3. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-method ready <step> <id>...`. On exit 1, stop and report each line it
   printed as what is missing, and never write the artifact anyway. On exit 3,
   report the record as not checked and stop.
4. Read `${CLAUDE_SKILL_DIR}/steps/<step>.md` and follow it.
5. Write each artifact from the template `${CLAUDE_SKILL_DIR}/../../bin/meow-method template <kind>` prints, as a
   draft, because approval is a person's act and not yours.
6. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-method check` and fix what it reports, for at most two rounds, and
   report anything still open after the second.
7. End by naming the artifact you wrote, the gate it now waits at, and the
   step that picks it up, with the command that runs it.
</steps>

<rules name="every step">
- M1. Do this step's work and no later step's, because a later step run early
  builds on an input nobody approved.
- M2. Ask at most three clarifying questions. For anything else unknown,
  choose a default, and record it in the artifact as a choice you made,
  because an unrecorded default can't be told from a gap nobody noticed.
- M3. Name what an artifact came from as bare identifiers in its front matter,
  never as links, and only in the upward direction, because what cites it is
  computed.
- M4. Where the record and the work disagree, report it and fix the artifact,
  because an artifact that has drifted from the tree gets cited as true.
- M5. Stop after writing an artifact that needs approval, and report the gate
  it waits at, because the next step built on an unapproved input inherits a
  decision nobody made.
- M6. Never take silence, a change of subject or an unrelated instruction as
  approval: only a person saying so approves, because an inferred approval is
  one nobody gave.
- M7. Before you write, search the record with `meow-method find` and a few
  specific words, several independent searches at once, and read a whole
  artifact with `meow-method show` only when its heading is relevant, because a
  search after writing is a consistency check and one before changes the
  answer.
- M8. Follow a decision the search finds, or amend it through its own record,
  and never ignore it, because an ignored decision is one the record says holds
  and the work says doesn't.
- M9. Write a durable finding back into the artifact it belongs to, because the
  record is the only memory the method keeps, and a finding left in the
  conversation is lost with it.
</rules>
