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
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-method status` and show its output.
2. Choose what to advance: the record named in `$ARGUMENTS` if one is, and
   otherwise the first decision whose line begins `next:`.
3. Where nothing begins `next:` and something waits for approval, report the
   first item waiting and stop, saying the chain is waiting on it.
4. Load the `method` skill and run the step the chosen line names, with its
   input.
5. Stop where that step ends at an approval gate.
6. Report which step you reached, why you stopped, and what the next
   invocation of `/meow-method:run` will do.
</steps>
