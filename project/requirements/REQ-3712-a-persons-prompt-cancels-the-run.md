---
id: REQ-3712
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3712

A prompt a person sends while a run is active, other than the start command, MUST end the run as cancelled, recording that the person cancelled it and when.

A Stop hook doesn't fire on an interrupt, so after `Esc` the run's state stays active and the hook would restart the run at the end of the person's next turn (RES-0320, conclusion 7). Ending the run on the next prompt keeps a person in control without a second command.
