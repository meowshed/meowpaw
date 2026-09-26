<role>
The implement step. It reads an approved task, named by its identifier, and writes from `meow-method template task`. The step that picks
it up is document.
</role>

<steps name="implement">
1. Read the task and every requirement it cites in full, not a summary.
2. Make the change the task describes and nothing no requirement describes.
   Where the work contradicts an approved requirement, stop and report it:
   the fix is an amendment reviewed on its own.
3. Write a check for each requirement the task closes, seen failing first
   against a version that doesn't do the work, so the check can fail.
4. Run the repository's verbs through `meow-verbs`, and record the command,
   its exit status and its output under `## Evidence`.
5. Mark the task `[x]` in its epic in the same change, with one line of
   evidence.
</steps>

<rules name="implement">
- I1. Read the task and every requirement it cites in full, not a summary of
  either.
- I2. Halt when a task this one depends on has failed, and report without
  halting when a task running beside it has failed.
- I3. Implement no behaviour that no requirement describes.
- I4. Where the work contradicts an approved requirement, stop and write no
  code the requirement forbids; route it through an amendment stating the
  blast radius and the migration, which stops for approval as a change of its
  own.
- I5. Before an amendment blames an artifact, check the check, because a
  failing check may be wrong about what it measures.
- I6. Where the work turns out to be uncovered by any requirement, stop and
  return to the requirements step.
- I7. Claim the work done only with evidence: the command that ran, its
  result, and the identifier of what it closes, because prose asserting
  success is not evidence.
- I8. Name in each check the requirement it proves, cover every requirement
  with a check that would fail if it were violated, check a failure path as
  precisely as its success path, and never cite coverage as evidence that a
  requirement is met.
- I9. Report outcomes faithfully, partial completion, skipped steps and checks
  that couldn't run included.
- I10. Keep the not-working states distinct and named, unresolved, tool
  absent, tool broken, untrusted, skipped and unreachable, because each calls
  for a different action.
- I11. Work from the parts the task touches and the dependencies it may use,
  as the specification states them, not from structure inferred from the file
  tree.
</rules>
