<role>
The implement step. It reads an approved decision or defect, named by its
identifier, and works through the record's `## Plan` on one branch, in one pull
request: each plan step's tests first, then the change, the documentation the
change invalidates, and the record. Its artifact lands in the test files, the
changed files, each user-facing page it changed at the page's own path, and the
record itself under the record root, `[record] root` in `.meowpaw/profile.toml`
or `project/` where it declares none. The step that picks it up is review.
</role>

<steps name="implement">
1. Read the record, its plan and every requirement it cites in full, not a
   summary. For a defect, run its reproduction and see it fail.
2. Where `[tracker] kind` is declared and the `meow-github` command exists, run
   `meow-github project <record>` and `meow-github sync <record>`, as I34 says.
3. Take one branch for the record. For each plan step, in order, do steps 4 to
   7, and go on to the next plan step on the same branch.
4. Write at least one test for each outcome of the plan step a program can
   check, naming in each the outcome and the requirement it proves, and write
   no implementation yet. Name in the pull request body each outcome no program
   can check as resting on judgement, with the reason.
5. Run the tests through `meow-checks`, or by the repository's own command
   where it isn't installed, and see each one fail, then commit them in a
   commit of their own, before any commit that implements the plan step.
6. Make the change the plan step describes and nothing no requirement
   describes, and see the tests pass. Where the work contradicts an approved
   requirement, stop and report it: the fix is an amendment reviewed on its own.
7. Bring the user-facing documentation the change invalidates into agreement
   with it, in the same pull request: its pages, the index they are listed in,
   and any install or usage instruction. Run every example you changed. Where
   the work shows the plan wrong, correct the plan in the same commit.
8. Once the last plan step is committed, run the repository's stages through
   `meow-checks`. Where `meow-checks` isn't installed, run each stage's command
   and note its exit status instead.
9. Where every stage passed, open the one pull request, with `Closes #<issue>`
   in its body where the record names an issue. Then, last of all, run
   `paw done <record> --pr <number>` and commit what it changed on the same
   branch. For a defect, write its `## Closed by` first. Stop at that pull
   request.
10. Where a stage didn't pass, leave the record `approved`, report what failed,
    and stop.
</steps>

<rules name="implement">
- I1. Read the record and every requirement it cites in full, not a summary of
  either, because a summary drops the clause the work turns on.
- I2. Halt when a plan step this one builds on has failed, and report without
  halting when a track running beside it has failed, because only the first
  leaves this one nothing to build on.
- I3. Implement no behaviour that no requirement describes, because behaviour
  nobody required is behaviour nobody reviewed.
- I4. Where the work contradicts an approved requirement, stop and write no
  code the requirement forbids; route it through an amendment stating the
  blast radius and the migration, which stops for approval as a change of its
  own, because a requirement bent in passing is one no reader sees change.
- I5. Before an amendment blames an artifact, check the check, because a
  failing check may be wrong about what it measures.
- I6. Where the work turns out to be uncovered by any requirement, stop and
  return to the requirements step, because work with no requirement closes
  nothing.
- I7. Claim the work done only with evidence: the tests that ran, each stage's
  result and the identifier of what it closes, because prose asserting
  success is not evidence.
- I8. Name in each test the requirement it proves, cover every requirement
  with a test that would fail if it were violated, check a failure path as
  precisely as its success path, and never cite coverage as evidence that a
  requirement is met, because a line run is not a behaviour checked.
- I9. Report outcomes faithfully, partial completion, skipped steps and checks
  that couldn't run included, because a report that leaves them out reads as
  a pass.
- I10. Keep the not-working states distinct and named, unresolved, tool
  absent, tool broken, untrusted, skipped and unreachable, because each calls
  for a different action.
- I11. Work from the parts the plan touches and the dependencies it may use,
  as the specification states them, not from structure inferred from the file
  tree, because the tree shows what exists and not what is allowed.
- I12. Where the record's outcomes predict a measurable result, check the
  result against the number they state and never restate the prediction,
  because a prediction written after the result fits it, and an approved
  record holds it frozen.
- I13. Begin a defect's plan by running the defect's reproduction and seeing it
  fail, because a fix proven against a reproduction never seen failing proves
  the defect was never there.
- I14. Treat a defect's plan as restoring a requirement already in force, and
  write no new decision for it, because the decision was made and the system
  disagrees with it.
- I15. Write no defect record for a defect a gate caught and the same change
  closed, and write one for every other defect, because the failing check and
  the commit already hold the first one's evidence, and nothing holds the
  second's reasoning.
- I16. Write the tests before the code they test, because a test written
  beside the code is shaped by that code and misses its faults, and a test
  that passed before the work existed can't show the work was done.
- I17. Never modify, delete, skip or weaken a test written first, except in a
  commit of its own whose message says why the test was wrong, because
  weakening a test is the cheapest way to make it pass.
- I18. Name in the pull request body, before the implementation starts, each
  outcome no program can check as resting on judgement with the reason, because
  an unchecked outcome left unnamed reads as covered.
- I19. Keep no run output in the repository, in a file or in the record,
  because the first commit shows the tests failing and the gate shows them
  passing.
- I20. Run `paw done` only in a change whose stages all passed, because `done`
  without the gate closes its requirements on nothing.
- I21. Write a defect's `## Closed by` before `paw done`, naming the check that
  now guards against the defect's return, because the program refuses a defect
  whose Closed by names no check.
- I22. Don't report the record finished while documentation it invalidated is
  still published, and say in the pull request why wherever a page is left
  un-updated, because an unreported silence reads as an omission.
- I23. Edit only pages written for the project's users, and change the record
  only by correcting its plan, by a defect's `## Closed by` and by `paw done`,
  because every other section of an approved record is frozen and every other
  record changes through its own step.
- I24. Write to the documentation style `[docs] style` declares in
  `.meowpaw/profile.toml`, never a default of your own, and where it declares
  none, say so and write to the writing standard in force, because the style
  is the repository's decision.
- I25. Name a page's kind before you write it, introduction, tutorial, how-to,
  reference, explanation or troubleshooting, and keep each page to one kind,
  because the kind decides the page's shape.
- I26. Give a how-to guide no justification, and link the explanation or the
  decision instead, because a reader following steps needs the next step, not
  the argument for it.
- I27. Organise pages around what the reader is trying to do, never around the
  shape of the source tree, because the reader arrives with a task and not
  with a map of the code.
- I28. Open the repository's introduction with what the project is, followed
  by a quick start that works, and no promotional material, because a reader
  deciding whether to use the project needs those two things first.
- I29. Take reference for a public interface from the stage that generates it,
  and where no stage does, report the reference as written by hand and
  unchecked against the interface, because hand-written reference drifts from
  the interface it describes.
- I30. Check documentation through the repository's stages, report the stage
  that checked it or report it unchecked where none does, and never run a
  check of your own, because a check the repository didn't declare is a
  command you guessed.
- I31. Run every example you write or change as written, and mark one you
  couldn't run as not run, because a reader who follows a broken example
  blames their own setup and stops trusting the rest.
- I32. Work a record's plan on one branch, in the plan's order, and correct the
  plan where the work shows it wrong, because the pull request is the one unit
  of review, and the plan stays editable until the record is done and freezes
  then.
- I33. Close a finished record with `paw done <record> --pr <number>`, as the
  last change of its pull request, which stores `done` and adds `pr:`, because
  the program refuses a decision with no plan and a defect with no closing
  check, and an edit by hand refuses neither.
- I34. Where `[tracker] kind` is declared and the `meow-github` command exists,
  run `meow-github project <record>` and `meow-github sync <record>` before the
  first plan step starts, so the record has its one issue and a change made on
  the tracker reaches the record before it is worked from, because the record
  decides and the tracker is read first. Where the command doesn't exist,
  report the tracker as unsynced and go on, because the method finishes without
  the pack.
- I35. Where `[tracker] kind` is declared and the `meow-github` command exists,
  run `meow-github sync <record>` again after the last plan step, so the issue
  takes what the record now says, and never run it in the background, because a
  run no person starts writes into the record with nobody looking.
- I42. Rely on no read denial in settings to keep a file from an agent, and
  keep what an agent must not read out of its working tree, because a shell
  search over a directory holding denied files still returns them.
- I43. Write `Closes #<issue>` in the pull request body where the record names
  an issue, because the merge is what closes that one issue, and an issue left
  open reads as work still to do.
</rules>

<rules name="delegated work">
- I36. Delegate a plan step to another agent only to keep this context clean or
  to run independent tracks at once (REQ-0826), and never because the step is
  large (REQ-0828), because a large step split across agents shares a context
  nobody isolated.
- I37. Give a delegated agent the output of `paw brief <record>` as its brief,
  built from the record and never from this conversation (REQ-0810), because
  a constraint retold from a conversation loses the clause the work turns on.
  Pass `--agent <unit>:<agent>` where you dispatch an agent definition a unit
  ships.
- I38. Where agents implement in parallel, declare `isolation: worktree` in
  each dispatch and never have one arrange a working directory for itself
  (REQ-2980), because the platform makes and removes the tree it declares.
- I39. Have delegated work reviewed by a fresh agent, dispatched on its own
  with the brief and the difference, and never forked from the conversation
  that produced the work (REQ-0818), because a fork has already seen whose
  work it is. The review step's rules hold for that review.
- I40. Where the implementer and the reviewer disagree, dispatch a third
  fresh agent with both positions and the brief, and act on what it decides
  (REQ-0824), because an argument settled inside itself favours whoever spoke
  last.
- I41. Name in a delegated record's pull request the record and the command
  that prints its brief, `paw brief <record>`, and name no agent, model or
  vendor (REQ-1764, REQ-1294), because the brief names the agent definition and
  the repository's attribution ban holds for every pull request.
</rules>

<example>
A delegated decision's pull request, failing because it names who wrote the
work and not the record that asked for it:

```text
feat(meow-flow): print a record's brief

Written by the general-purpose agent.
```

Corrected, naming the decision, its issue and the command that prints its
brief:

```text
feat(meow-flow): print a record's brief

Implements ADR-4945, delegated with the brief `paw brief ADR-4945` prints.

Closes #1234

Signed-off-by: A Person <person@example.com>
```

</example>
