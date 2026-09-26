<role>
The document step. It reads an epic whose tasks are all done, named by its identifier, and writes from `meow-method template spec`. The step that picks
it up is verify.
</role>

<steps name="document">
1. Bring the user-facing documentation into agreement with what the epic
   changed: pages, the index they are listed in, and any install or usage
   instruction the change invalidated.
2. Report what you changed and what you deliberately left alone, with the
   reason, because an unreported silence reads as an omission.
</steps>

<rules name="document">
- O1. Bring the user-facing documentation into agreement with what the epic
  changed.
- O2. Report what you changed and what you deliberately left alone, and record
  the reason wherever documentation is left un-updated, because an unreported
  silence reads as an omission.
- O3. Don't report an epic finished while documentation its tasks invalidated
  is still published.
</rules>
