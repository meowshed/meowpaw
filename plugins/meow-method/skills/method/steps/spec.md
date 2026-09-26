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
