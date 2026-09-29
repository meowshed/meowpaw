<role>
The implement step. It reads an approved task, named by its identifier, and
writes from `paw template task`. Its artifact lands in the changed files, the
kept runs under the evidence directory, `evidence_dir` under `[verbs]` or
`evidence` under the record root, and the `## Evidence` of
`tasks/TSK-NNNN-<slug>.md` under the record root, `[record] root` in
`.meowpaw/profile.toml` or `project/` where it declares none. The step that
picks it up is document.
</role>

<steps name="implement">
1. Read the task and every requirement it cites in full, not a summary.
2. Make the change the task describes and nothing no requirement describes.
   Where the work contradicts an approved requirement, stop and report it:
   the fix is an amendment reviewed on its own.
3. Run the checks the cover step wrote, which the task's `## Cover` names,
   and see each one pass, because a cover check still failing shows the work
   isn't done.
4. Run the repository's verbs through `meow-verbs`, then
   `meow-verbs evidence` on them, and cite each result under `## Evidence` as
   it printed: the verb, the outcome, the record and the tree id, and keep
   each cited record with `meow-verbs evidence --keep`, citing the kept path.
   Where `meow-verbs` isn't installed, record the command, its exit status and
   its output instead.
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
  result, its record and tree id where `meow-verbs` recorded it, and the
  identifier of what it closes, because prose asserting success is not
  evidence, and a result with no tree id can't show which content it checked.
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
- I12. Where the task predicts a measurable outcome, write the predicted number
  under Acceptance criteria before the work starts, because a prediction
  written after the result fits it, and an approved task holds it frozen.
- I13. Begin a task a defect authorises by running the defect's reproduction
  and seeing it fail, because a fix proven against a reproduction never seen
  failing proves the defect was never there.
- I14. Treat a defect's task as restoring a requirement already in force, and
  write no new decision for it, because the decision was made and the system
  disagrees with it.
- I15. Write no defect record for a defect a gate caught and the same change
  closed, and write one for every other defect, because the failing check and
  the commit already hold the first one's evidence, and nothing holds the
  second's reasoning.
</rules>
