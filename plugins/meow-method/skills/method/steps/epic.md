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
