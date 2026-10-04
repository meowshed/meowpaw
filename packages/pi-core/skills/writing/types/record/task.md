<role>
A task is one unit of work: one branch, one change, one review.
</role>

<rules name="sections, in order">
1. What to do: What to do, in enough detail for an implementer with no access
   to the
   conversation, with the constraints that bind it.
2. Depends on: What it depends on, one task to a line, each marked
   `(blocking)` or `(not blocking)` with why; a dependency that is only
   convenience is declared as not blocking, never left out.
3. Evidence: The evidence once done: the command, its result, and the change
   that carried it.
4. Left alone: What it left alone, such as documentation deliberately not
   updated, and why.
</rules>

<rules name="done">
It is done when somebody else could verify it from its evidence alone.
</rules>
