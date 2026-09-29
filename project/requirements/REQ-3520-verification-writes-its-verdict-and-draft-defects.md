---
id: REQ-3520
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0063, RES-0309
verification: static
---

# REQ-3520

**Withdrawn by ADR-2300.**

It read: verification MUST write nothing into the repository except three things: the epic's `## Verified` section, the epic's `checked-at` field naming the issue the verification ran under, and a draft defect record for each refutation it confirms.

Verification leaves the code, the requirements and the specification alone,
because a step that both detects a divergence and repairs it repairs it in the
cheap direction, which is to reword the specification until the divergence
disappears (RES-0063). A confirmed refutation is evidence that a requirement
isn't met, and evidence left only in a report is lost with the conversation,
so it may land as a draft defect, which authorises nothing until a person
approves it. Verification changes no stored `status`, because the statuses a
task or an epic stores record a person's decision, and the observed statuses
`verified` and `done` are derived from `## Verified` and `checked-at`.

ADR-2300 removes the verification step and the skeptic, so no step is left for this rule to bind.
