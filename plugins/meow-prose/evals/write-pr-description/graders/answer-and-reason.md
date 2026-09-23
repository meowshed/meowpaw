---
type: llm
focus: last_message
weight: 2
---

Judge whether the text leads with its answer and gives each decision its reason.

A title line, such as a Markdown heading naming the change, is allowed and is not the first sentence; judge the first sentence after it.

PASS when the first sentence states the change or the decision itself, and every decision in the text carries its reason in the same or the next sentence.

FAIL when the first sentence gives background or a preamble before the answer, or when a decision appears with no reason.
