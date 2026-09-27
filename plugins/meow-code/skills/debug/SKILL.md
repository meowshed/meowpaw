---
name: debug
description: How a defect is debugged in this repository. It MUST be loaded before looking for the cause of any bug, failing check, crash or wrong output, including one that looks obvious. It MUST NOT be skipped, however quick the fix seems.
---

<role>
You find why the system misbehaves by observing it, not by reading a story
into the code. A cause offered before the defect is reproduced is a guess, and
a fix proven by a check that never failed proves nothing.
</role>

<steps name="debug">
1. Reproduce the defect, as small as you can make it, and keep the
   reproduction as a check.
2. Record what the system actually does: the output, the error, the value.
3. Name one hypothesis that could be false, and try to refute it.
4. When the hypotheses run out, bisect: halve the inputs, the change or the
   history until the defect's edge is found.
5. Fix the cause, run the reproduction, and show it failing before the fix
   and passing after it; stop there, or report the symptom you only treated.
</steps>

<rules name="debugging">
- G1. Begin by reproducing the defect as small as it can be made, and keep
  the reproduction, because an unreproduced defect can't be shown fixed and a
  discarded one can come back unnoticed.
- G2. Record what the system actually does before you offer a cause, because a
  cause offered before an observation is a guess with a narrative.
- G3. Hold one falsifiable hypothesis at a time, and test it by trying to
  refute it, because with two at once neither is tested.
- G4. Bisect once the hypotheses run out, and stop guessing, because halving
  the search space always ends and another guess may not.
- G5. Close the defect with the reproduction seen failing before the change
  and passing after it, because a reproduction never seen failing proves the
  defect was never there.
- G6. Fix the cause, and say so plainly where you treated only the symptom,
  because a symptom fixed quietly is a defect that returns with its evidence
  gone.
- G7. Where the defect shows a requirement to be wrong, stop and route it
  through an amendment, and patch nothing, because a patch against a wrong
  requirement makes the code disagree with what the record says it must do.
</rules>
