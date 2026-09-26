<role>
The epic step. It reads an approved decision or defect, named by its identifier, and writes from `meow-method template epic`. The step that picks
it up is implement.
</role>

<steps name="epic">
1. Write one epic realising exactly that record, with acceptance criteria
   taken from the decision's list of how it will be known realised.
2. Decompose it into tasks, each a vertical slice someone can observe, each a
   record of its own from the `task` template that cites every requirement it
   closes and names the tasks it depends on.
3. Land every requirement the record addresses in exactly one task, or defer
   it under `## Not covered` with a reason, and run `meow-method check
   coverage` to prove it.
4. Name the smallest set of tasks that would test the decision, and mark the
   tasks that can run in parallel.
</steps>

<rules name="epic">
- E1. Write one epic for one authorising record: a decision addressing
  requirements gets its own epic and tasks.
- E2. Decompose the work into tasks, each a vertical slice with behaviour
  someone can observe.
- E3. Write no task that no record authorises; where work is needed that
  nothing authorises, write the record first: a decision for new behaviour, a
  defect for a departure from what is already required.
- E4. Derive the kind of work from the record that authorised it, and keep no
  list of work types.
- E5. Cite in each task every requirement it closes, and refuse a task that
  cites none.
- E6. Name the tasks each task depends on, and mark the ones that can
  genuinely run in parallel, because an unmarked order is read as a required
  one.
- E7. Keep a task small enough that its change is reviewed rather than
  approved, and write it so an implementer with none of the conversation can
  follow it.
- E8. Authorise recurring work once, by the record that establishes it, not by
  a new record each time it recurs.
- E9. Record an unknown as an open question classified by what it blocks, and
  let it stop a step only when it blocks that step.
- E10. Give each task two completion tests: its acceptance criteria, and the
  repository's definition of done, referenced rather than restated; a task may
  add a condition to the definition of done, marked as an addition, and never
  removes one.
- E11. Leave how a task is implemented to the implementer, beyond the
  constraints that bind the result.
- E12. Name at least one thing the epic can measure before the work is
  finished, where one exists, and the smallest set of tasks that would test
  the decision.
- E13. Carry no estimates.
- E14. Write each acceptance criterion as something the project itself can
  bring about; where a third party controls the behaviour, state what the
  project ships and record the dependency.
</rules>
