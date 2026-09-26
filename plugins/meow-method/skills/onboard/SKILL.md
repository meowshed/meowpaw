---
name: onboard
description: Brings an existing repository's documents into the method, recovering its vision, specifications and constitution, and stops at an onboarding report for approval.
disable-model-invocation: true
---

<role>
You record what a repository already is, from what it already holds, and
invent nothing, because a record reconstructed from code states what a system
does as though somebody had decided it must.
</role>

<steps name="onboard">
1. Run `meow-verbs status` where that unit is installed, and note which verbs
   resolve; where `.meowpaw/profile.toml` is missing, stop and say to run
   `/meow-method:init` first.
2. Read the repository's documentation, any harness it already has, and its
   code, in that order. Where the `meow-github` command exists, run
   `meow-github history` and read its issues, pull requests and comments as
   well.
3. Write the vision, one specification per part of the system, each
   requirement and decision the documents and the history state, and, where
   the repository has no `CLAUDE.md`, the constitution, from the templates
   `${CLAUDE_SKILL_DIR}/../../bin/paw template <kind>` names.
4. Write `onboarding.md` at the record's root from
   `${CLAUDE_SKILL_DIR}/../../bin/paw template onboarding`, as a
   draft.
5. Run `${CLAUDE_SKILL_DIR}/../../bin/paw check` and fix what it
   reports in what you wrote.
6. Report the verbs, the gaps and the disposition of every document, and stop.
   Say that once the report is approved,
   `${CLAUDE_SKILL_DIR}/../../bin/paw onboarding remove` removes what it
   placed.
</steps>

<rules name="onboard">
- B1. Produce the method's artifacts from what the repository holds: its
  documentation, its existing harness and its code, because onboarding
  records what a repository is and leaves what it should be to the steps
  that follow.
- B2. Recover the vision, the specifications and a missing constitution, and
  nothing else, because those describe the present and can be read from it.
- B3. Write no requirement and no decision, because code shows what a system
  does and never what it must do, nor which alternatives lost; each
  obligation you notice goes to the gaps as a question.
- B4. End every recovered statement with the file it came from, as
  `(from <path>, <confidence>)`, and drop a statement you can't trace to a
  file instead of softening it, because an untraced statement reads as fact.
- B5. Give each recovered statement a confidence: high where a file states it,
  medium where the code shows it consistently, low where you inferred it,
  because a reader weighs a statement by how it was found.
- B6. Put everything you couldn't determine in the report's Gaps section, each
  as a question a person can answer, because an omitted gap reads as
  something known.
- B7. Read an existing harness in full before placing it, and cite it or
  migrate it, never discard it unread, because its principles carry the
  defects that justify them and nothing in the code does.
- B8. Report each convention you observe as how often it appears and offer it
  as a decision, never as a rule, because what a repository does most often
  is a habit and not a rule somebody chose.
- B9. Rewrite no existing file, and delete none before the report placing it
  is approved, because the repository adopted nothing yet.
- B10. Stop at the report as a draft, handing over the gaps and the
  disposition of every document, and wait for approval, because a person
  decides what the repository becomes.
- B11. Migrate a record the repository keeps in a format of its own, such as a
  folder of decision records or a task list, to the artifact kind that holds
  it, one artifact per record, because left in its old format it is a second
  record and the strongest evidence of what was decided.
- B12. Write every requirement and decision you recover as a draft, because a
  person's approval is what affirms it, never the step that recovered it.
- B13. Recover a draft requirement for each obligation a document, an issue or
  a pull request states, citing the file, or the issue or comment by its
  address, and none from code alone, because a person wrote the obligation
  down and code states only what the system does.
- B14. Recover a draft decision for each choice a document, an issue or a pull
  request records with the alternative it rejected, citing the discussion,
  and read a pull request closed without merging as a rejected alternative,
  because code keeps only the option that won.
- B15. Where the `meow-github` command doesn't exist, report the forge history
  as unread in the report's gaps and name `meow-github` as the pack that
  would read it, because history left unread reads as history holding
  nothing.
</rules>
