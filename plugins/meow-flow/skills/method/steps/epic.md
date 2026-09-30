<role>
The epic step. It reads an approved decision or defect, named by its
identifier, and writes from `paw template epic`. Its artifact lands in
`epics/EPC-NNNN-<slug>.md` and one `tasks/TSK-NNNN-<slug>.md` for each task,
under the record root, `[record] root` in `.meowpaw/profile.toml` or
`project/` where it declares none. The step that picks it up is implement.
</role>

<steps name="epic">
1. Where one task realises the decision, write that task alone, naming
   `realises: ADR-NNNN` in place of `epic:`, with the decision's criteria as
   its own, and stop. Otherwise write one epic realising exactly that record,
   with acceptance criteria taken from the decision's list of how it will be
   known realised.
2. Decompose it into tasks, each a vertical slice someone can observe, each a
   record of its own from the `task` template that cites every requirement it
   closes and names the tasks it depends on.
3. Land every requirement the record addresses in at least one task, or defer
   it under `## Not covered` with a reason, and run `paw check
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
- E7. Write each dependency on its own line marked `(blocking)` or
  `(not blocking)`, and declare one that exists only for convenience as not
  blocking with its reason rather than leaving it out, because `paw` waits on
  an unmarked line and the implementer of the second task needs the reason
  the two touch.
- E8. Keep a task small enough that its change is reviewed rather than
  approved, and write it so an implementer with none of the conversation can
  follow it.
- E9. Authorise recurring work once, by the record that establishes it, not by
  a new record each time it recurs.
- E10. Record an unknown as an open question classified by what it blocks, and
  let it stop a step only when it blocks that step.
- E11. Give each task two completion tests: its acceptance criteria, and the
  repository's definition of done, referenced rather than restated; a task may
  add a condition to the definition of done, marked as an addition, and never
  removes one.
- E12. Leave how a task is implemented to the implementer, beyond the
  constraints that bind the result.
- E13. Name at least one thing the epic can measure before the work is
  finished, where one exists, and the smallest set of tasks that would test
  the decision.
- E14. Carry no estimates, because an estimate in a record is read as a
  promise.
- E15. Write each acceptance criterion as something the project itself can
  bring about, and as something the task's or the epic's own work decides,
  never a later epic's; where a third party controls the behaviour, state
  what the project ships and record the dependency, because a criterion that
  waits on other work can't be met when it is checked.
- E16. Write no epic for a decision one task realises, because an epic
  holding one task is a second record for the same plan.
- E17. Let a task close several requirements and several tasks close one,
  because a requirement often needs a program change and a prompt change.
</rules>
