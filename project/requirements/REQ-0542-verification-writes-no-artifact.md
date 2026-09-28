---
id: REQ-0542
artifact: requirement
topic: artifacts
class: functional
status: withdrawn
revised: 2026-09-28
elaborates: RES-0063
verification: static
---

# REQ-0542

**Withdrawn by ADR-2200, in the change that approved ADR-2200 and REQ-3520.
Replaced by REQ-3520.**

It read: verification MUST write no artifact into the repository. What it
leaves behind is a change of status on the task it checked and on the epic
that task belongs to; what it reports, it reports to the person. Its reason
was that deciding whether the code or the requirement is wrong belongs to a
person (RES-0063).

REQ-3524 asks verification to record each refutation it confirms as a draft
defect, which this rule forbade. Under it, REQ-3170's recorded defect existed
only where a person filed it, and otherwise only in the conversation. REQ-3520
also approves the epic's `## Verified` section and its `checked-at` field,
which this wording forbade and which verification already wrote. ADR-2200
gives the reasoning, and REQ-3520 keeps the rule that verification repairs
nothing and names the three things it may write.
