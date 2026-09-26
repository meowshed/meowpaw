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

<rules name="verify">
- V1. Keep checking the record, which `meow-method check` does on every
  change, apart from verifying the work, which is this step, and never report
  one's failure as the other's.
- V2. Modify no code, requirement or specification, and write no new artifact;
  offer remediation and don't apply it.
- V3. Verify a task when it claims to be done, asking only whether its
  evidence closes the requirements it cited; evidence that names no
  requirement closes nothing, and the task is unproven rather than failed.
- V4. Never reconcile a claim against evidence collected before the current
  revision: collect it again by running the verbs, rather than inferring that
  nothing relevant changed.
- V5. Verify an epic when its tasks are done, as the sum of them, asking
  whether its authorising record is realised, never by verifying each task
  again, and never merely because the tasks are done.
- V6. Treat a requirement as unrealised while any decision addressing it is
  unrealised, and report one realised only in part.
- V7. Report a requirement the record addresses that no task closes as a gap,
  and never add a task for it silently; revisit every requirement deferred
  with a reason.
- V8. Judge whether each check would fail if its requirement were violated,
  and report one that wouldn't.
- V9. Record the outcome as a status on the task or the epic, with every gap
  reported, and report every way the work and its artifacts disagree, worst
  first.
- V10. Stop at whether the decision was realised, and don't ask whether it was
  right, because its reversal condition answers that on later evidence.
- V11. Check an architectural property a program can settle rather than
  reviewing it, assess one no program can settle as a declared judgement, and
  never report passing checks on single properties as an architectural pass.
</rules>
