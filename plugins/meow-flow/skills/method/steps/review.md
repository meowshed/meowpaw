<role>
The review step. It reads a task's pull request, and writes nothing into the
repository. The pull request fixes what the review finds. The step that picks
it up is none, the chain ends here.
</role>

<steps name="review">
1. Read the difference of the task's pull request against the base it was
   opened on, and the task and the requirements it closes.
2. Where this session produced the change, dispatch the review to an agent
   with read-only tools, giving it the difference and what the task asks and
   not who wrote it, and read its return as a verdict.
3. Judge conformance to the requirements and the quality of the work
   separately. Try to refute each finding before reporting it, and state its
   kind in its first clause.
4. Report each test in the change that would still pass against a wrong
   implementation.
5. Where the change touches documentation, judge each changed page against
   the kind it names, and follow a changed quick start from an empty
   directory.
6. Order findings worst first, mark a preference as one, and report a clean
   result as clean in one sentence.
7. Where a finding stands, fix it in that pull request, and say in the task's
   Evidence what the review found, in a sentence. Write nothing else into the
   record, and stop when the gate passes again.
</steps>

<rules name="review">
- W1. Spend findings on what a reader can see and a check can't, because
  passing checks are no substitute for review and a check already settles the
  rest.
- W2. Read the difference against a recorded base, not against whatever the
  branch sits on now.
- W3. Judge conformance to the requirements and the quality of the work
  separately, because correct but wrong is still wrong.
- W4. Name in each finding the input or condition that makes the work wrong,
  and ask as a question anything you can't name that way; try to refute each
  finding before reporting it.
- W5. State each finding's kind in its first clause, mark a preference as a
  preference, and order findings worst first.
- W6. Report a clean result as clean in one sentence, and manufacture no
  finding when there is none.
- W7. Approve work that improves the state of the codebase, and don't withhold
  approval because it could be better.
- W8. End in one verdict from a fixed set, finished or returned to implement.
- W9. Post findings to the review system only when asked, and write nothing
  into the record but the sentence step 7 names, because a finding fixed
  beside its cause needs no record.
- W10. Name the parts the change touches and the dependencies it adds, because
  a structural regression is invisible in a diff by construction.
- W11. Follow a changed quick start from an empty directory, and where you
  can't, report that you read it and didn't run it, because the defect a
  quick start most often carries is a prerequisite nobody stated, and only
  following it finds that.
- W12. Judge each changed page against the kind it names, and report a page
  that serves two kinds or a how-to that justifies itself as a finding,
  because no program can tell a page's kind from its text.
- W13. Where no agent can be dispatched for a change this session produced,
  report the verdict as self-assessed, because a model judging its own output
  is biased in a direction capability doesn't correct.
- W14. Name the verdict as an agent's, never as a person's approval, because
  an agent covers more than a person and can't answer whether the work should
  exist.
- W15. Report a test that compares a value with itself, mocks the thing under
  test, matches output loosely or searches with a pattern that can match
  nothing, and ask for it to be rewritten, never for a second test beside it,
  because the first goes on passing for the wrong reason.
- W16. Review the fixes once more with a fresh agent, at most twice in all, and
  report each finding still open after that to the person in the pull
  request, because a bound is what makes repair end and a dropped finding is
  one nobody decided.
- W17. Dispatch no agent to review a record, because the person approving the
  pull request reads it.
</rules>
