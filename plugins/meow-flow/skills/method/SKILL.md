---
name: method
description: The method's ten steps, research, requirements, design, spec, epic, cover, implement, document, verify and review, and the gate each checks. It MUST be loaded before any research, requirement, decision, specification, epic or task record is written, before a task is implemented, and before an epic is documented, verified or reviewed. It MUST NOT be skipped, however small the record looks.
---

<role>
You run one step of the method at a time. Each step writes one artifact from
an approved input, because an artifact built on an unapproved one inherits a
decision nobody made. A program settles whether the input is ready, and you
don't overrule it.
</role>

<steps name="run a step">
1. Name the step and the identifiers of its input. The steps, in order, are
   research, requirements, design, spec, epic, cover, implement, document,
   verify and review.
2. Read the repository's principles before producing anything: `CLAUDE.md`,
   and each file `.meowpaw/profile.toml` names under `[method] principles`.
3. Run `${CLAUDE_SKILL_DIR}/../../bin/paw ready <step> <id>...`. On exit 1, stop and report each line it
   printed as what is missing, and never write the artifact anyway. On exit 3,
   report the record as not checked and stop.
4. Read `${CLAUDE_SKILL_DIR}/steps/<step>.md` and follow it.
5. Write each artifact from the template `${CLAUDE_SKILL_DIR}/../../bin/paw template <kind>` prints, as a
   draft, because approval is a person's act and not yours.
6. Run `${CLAUDE_SKILL_DIR}/../../bin/paw check` and fix what it reports, for at most two rounds, and
   report anything still open after the second.
7. Dispatch the `meow-flow:record-reviewer` agent on each record you wrote,
   naming its path and nothing else, as M19 to M23 say.
8. End by naming the artifact you wrote, the gate it now waits at, and the
   step that picks it up, with the command that runs it, and say the record
   was reviewed by an agent and is unreviewed by a person.
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
- M7. Before you write, search the record with `paw find` and a few
  specific words, several independent searches at once, and read a whole
  artifact with `paw show` only when its heading is relevant, because a
  search after writing is a consistency check and one before changes the
  answer.
- M8. Follow a decision the search finds, or amend it through its own record,
  and never ignore it, because an ignored decision is one the record says holds
  and the work says doesn't.
- M9. Write a durable finding back into the artifact it belongs to, because the
  record is the only memory the method keeps, and a finding left in the
  conversation is lost with it.
- M10. Separate, in every report, what you verified from what you assumed, and
  name the command behind each verified claim, because an assumption reported
  beside a check reads as one.
- M11. Write an insight only when the work taught something that holds past
  its case, never because a step ended or a period passed, and report that
  nothing was learned as an ordinary outcome, because a log written on a
  schedule fills with activity and buries the few lessons in it.
- M12. Keep what happened, and when, in the version control history, and put
  only the lesson and its evidence in an insight, because the history already
  holds the activity and a second copy drifts from it.
- M13. Look for an insight with `paw find` when the work in front of
  you touches its subject, and never read the insights in bulk at the start,
  because retrieval earns its cost only where the work needs the lesson.
- M14. Change the record's shape by expand, migrate and contract: accept both
  forms, move every record, then remove the old form, and name the release
  that removes it when the new form arrives, because a removal nobody
  scheduled either never happens or surprises whoever still writes the old
  form.
- M15. Give a new obligation on records that already exist a migration in the
  same change, or add it as a draft rule, which grandfathers the approved
  records, and say which in the decision, because an approved record can't be
  changed to meet a rule written after it.
- M16. Edit front matter as structured data and a link as a link, never by
  text substitution, and where no parser exists make the migration smaller,
  not cleverer, because a substitution that matches the wrong text corrupts a
  record and nothing fails.
- M17. Split a migration into parts reviewed separately, by kind or by
  directory, with the mechanical part in a change of its own apart from the
  editorial part, because a rename can be checked and a rewritten paragraph
  can only be read.
- M18. Run `paw count` before and after a migration and put both
  outputs in its evidence, because a record the migration lost fails no other
  check.
- M19. Give the reviewer the record's path alone, never who wrote it or why,
  because a judge told which side it produced judges that side differently.
- M20. Fix what the reviewer finds and dispatch a fresh reviewer on the
  result, at most twice, because the second round catches what the first fix
  broke and a bound is what makes repair end.
- M21. Write each finding still open after the second round, and each finding
  you reject, into the record under `## Open review findings` with your reason,
  and name that section in the gate report, because the record is what
  outlasts the turn and what the person approving reads.
- M22. Where no agent can be dispatched, review nothing yourself: report the
  record as unreviewed by an agent or a person and stop at the gate, because a
  session judging its own record is the bias the review exists to avoid. Where
  a person asks you to review your own work anyway, report the result as
  self-assessed and unreviewed by a person.
- M23. Where the reviewer's output comes back marked as stopped at its turn
  ceiling, report the record as unreviewed by an agent, as M22 does for a
  review that couldn't run, because a partial list of findings reads as a
  complete one.
</rules>
