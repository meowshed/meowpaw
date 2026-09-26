<role>
The design step. It reads approved requirements, named by their identifiers, and writes from `meow-method template adr`. The step that picks
it up is spec.
</role>

<steps name="design">
1. Write one decision record per decision, addressing the requirements it
   settles by identifier. A decision that addresses none is refused.
2. Compare at least three alternatives, doing nothing among them, each with
   what it is genuinely better at and why it lost.
3. Record what it costs, what would reverse it as a condition, what it does
   not settle, and how anyone will know it was realised, written now.
4. Argue against it before you finish, and state the strongest objection.
5. Say what works once it is accepted and what still doesn't, so a reader can
   tell an increment from a promise.
</steps>

<rules name="design">
- D1. Write one decision record per decision, each naming by identifier the
  requirements it satisfies; a decision may settle several requirements, and a
  requirement may be settled by several decisions.
- D2. Ask first whether a program could settle the rule, and make a rule that
  must hold every time a check or a hook rather than a paragraph.
- D3. Title the decision with the decision itself, so a list of decisions
  reads as a list of positions.
- D4. State the non-goals under What this does not settle.
- D5. Where a draft can't say what the system does after it that it didn't
  before, merge it with its neighbours or split it by capability, not by
  component.
- D6. Argue against the decision before you record it, and state the strongest
  objection rather than summarising it away.
- D7. Critique the draft for what it doesn't say: repetition, concurrency, a
  failure after a failure, empty and enormous input, unnamed failure states,
  assumed ordering, and the assumption the operator won't notice.
- D8. Close with a premortem: what went wrong, written as though it already
  had.
- D9. Where elicitation runs out of ideas, fall back on these questions: who
  is the reader, what do they do today instead, what fails first, what is the
  smallest version that works, and what would make this decision wrong.
- D10. Where the system has an interface, you may write its contract and its
  rationale as separate artifacts, because different people read them.
</rules>
