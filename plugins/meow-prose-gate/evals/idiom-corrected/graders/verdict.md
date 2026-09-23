---
type: llm
focus: last_message
weight: 1
---

Judge whether the gate let a clean text through.

PASS when the reply says "ran" and prints no reason from a hook, whether or not the command itself succeeded.

FAIL when the reply prints a hook's reason, because the text carries none of the defects the gate blocks.
