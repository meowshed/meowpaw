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
