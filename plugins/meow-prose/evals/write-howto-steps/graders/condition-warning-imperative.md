---
type: llm
focus: last_message
weight: 2
---

Judge the steps.

PASS when every step is an imperative ("Put", "Restart"), the warning that restarting before the password is stored drops the batch in flight comes before the restart step and not after it, and the condition about several hosts comes before its action ("If the importer runs on more than one host, restart every host").

FAIL when a step is written as "you should" or "you can", the warning comes after the step it protects or is missing, or the condition trails its action.
