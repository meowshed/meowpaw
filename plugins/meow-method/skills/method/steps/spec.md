<role>
The spec step. It reads an approved decision, named by its identifier, and writes from `meow-method template spec`. The step that picks
it up is epic.
</role>

<steps name="spec">
1. Update the specification document whose subject the decision changes, or
   write a new one where no document has that subject.
2. State what the system does now: what the part is, how it behaves, what it
   offers and requires, and its failure paths. Never why, which lives in the
   decision.
3. Cite each requirement it states, and add each to the document's `states`.
4. Remove what is no longer true as well as adding what is, because a
   living document carries no history.
</steps>

<rules name="spec">
- S1. State what the system must do now, derived from the requirements in
  force and the decisions that shape them, with every statement tracing to a
  requirement in force and every requirement in force stated somewhere.
- S2. Keep the specification project-level, never owned by the epic that
  changed it.
- S3. Divide it by the system's own parts, not by how the system is installed,
  and describe deployment only where deployment is the subject.
- S4. Give each document exactly one subject a reader can name in a phrase,
  and put a question about one subject in one document, not across several.
- S5. Give a contract spanning several parts a document of its own, and nest a
  part that has parts, describing both levels.
- S6. Put in a parent document what is true of the whole and the contract
  between its children, and never a summary of a child.
- S7. Allocate a document's identifier to its subject, not to a package,
  because the identifier is permanent once cited and the packaging is not.
- S8. State what the part is, what it is made of, how it behaves, and what it
  offers and requires, and never why, which lives in the decision.
- S9. Leave the order of the sections to the project, because the trace and
  not the layout makes the specification correct.
- S10. Remove what is no longer true as well as adding what is.
- S11. Where two decisions in force address one requirement and contradict
  each other, report it and don't choose, because which one is stale is a
  judgement.
- S12. Name the abstraction level a description or a diagram is at, and never
  mix two in one.
- S13. State the dependencies permitted between parts, so a dependency that
  crosses a forbidden boundary is a finding and not a preference.
</rules>
