---
id: REQ-3201
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-28
elaborates: RES-0001
verification: static
---

# REQ-3201

**Withdrawn. Replaced by REQ-3203.**

It read: each step of the method MUST leave its artifact as a file committed to
the repository.

Review is one of the steps, and REQ-0544, approved before it, says review MUST
NOT produce an artifact in the repository. No design could meet both, so
REQ-3203 keeps the obligation for every step except review and narrows it to
what each step's instructions must name. A static check can read what the
instructions name, and it can't observe that a step committed anything, so the
outcome itself is no longer checked.

## Open review findings

- The agent reviewer noted that "Replaced by REQ-3203" reads as `superseded`
  in the constitution's vocabulary, where `withdrawn` names the decision that
  withdrew a record. I left it, because every requirement tombstone in the
  record uses `withdrawn` with "Replaced by", and changing this one alone
  would make it the only exception. The question belongs to the whole corpus.
- The agent reviewer suggested moving this section to the pull request body,
  so the review exchange doesn't freeze into a tombstone. I left it, because
  the workflow that writes this record keeps each finding it leaves in the
  record, where the next change to the corpus finds it.
