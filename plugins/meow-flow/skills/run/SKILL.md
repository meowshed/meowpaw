---
name: run
description: Drives the method's chain to its next approval gate, from the state the record shows.
argument-hint: "[record identifier]"
disable-model-invocation: true
---

<role>
You take the record to its next approval gate and stop there. You remember
nothing between runs, because the record is the state: run again after an
approval, you continue; run again with nothing approved, you say you are
waiting.
</role>

<steps name="drive the chain">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/paw status` and show its output.
2. Choose what to advance: the record named in `$ARGUMENTS` if one is, and
   otherwise the first decision whose line begins `next:`.
3. Where nothing begins `next:` and something waits for approval, report the
   first item waiting and stop, saying the chain is waiting on it.
4. Load the `method` skill and run the step the chosen line names, with its
   input.
5. Stop where that step ends at an approval gate. Where the person asked for
   a whole decision in one pull request, the method skill's M20 carries the
   steps through, and you stop at that pull request.
6. Where that step ends without an approval gate, run
   `${CLAUDE_SKILL_DIR}/../../bin/paw status` again and continue from step 2,
   because the next step's input is already approved.
7. Report which step you reached, why you stopped, and what the next
   invocation of `/meow-flow:run` will do.
</steps>
