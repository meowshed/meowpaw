<role>
The verify step. It reads an epic whose tasks are all done, named by its identifier, and writes from `meow-method template epic`. The step that picks
it up is review.
</role>

<steps name="verify">
1. Collect the evidence again at the current revision by running the verbs,
   because evidence from before an edit doesn't survive the edit.
2. Check each acceptance criterion against that evidence, and each
   requirement the decision addresses against the task that closes it.
3. Report every gap, worst first, as a gap: never add a task to cover it
   silently, and never modify code, requirements or the specification.
4. Where every criterion is met, write a `## Verified` section in the epic
   with the evidence per criterion, and set its `checked-at` to the issue the
   verification ran under.
</steps>
