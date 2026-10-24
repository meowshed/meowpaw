<role>
An epic realises exactly one decision or one defect, which is what gives it an
end.
</role>

<rules name="sections, in order">
1. Acceptance criteria: Acceptance criteria taken from the authorising record
   before the
   tasks were written, each stating what the project can bring about and never
   how a third party must behave.
2. Tasks: The tasks, each with what it closes and what it depends on, marked
   `(blocking)` or `(not blocking)`, and why, and none with a mark of its
   state, because a task's state is read from the task.
3. Coverage: The coverage check: every requirement the record addresses lands
   in exactly one task, or is deferred with a reason.
4. Not covered: What it leaves out, and why.
</rules>

<rules name="done">
It is done when its coverage check passes and every criterion is something the
project ships.
</rules>
