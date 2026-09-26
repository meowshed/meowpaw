<role>
The review step. It reads a verified epic, named by its identifier, and writes nothing into the repository. The step that picks
it up is none, the chain ends here.
</role>

<steps name="review">
1. Read the verification first, and spend findings only on what a check
   can't see.
2. Read the difference against a recorded base, not whatever the branch sits
   on now.
3. Judge conformance to the requirements and the quality of the work
   separately. Try to refute each finding before reporting it, and state its
   kind in its first clause.
4. Order findings worst first, mark a preference as one, and report a clean
   result as clean in one sentence.
5. End in one verdict: finished, or the step the work returns to. Write
   nothing into the repository, and post to the review system only when
   asked.
</steps>
