---
type: llm
focus: last_message
weight: 2
---

Judge the text for the patterns that have no reliable marker.

PASS when the text has none of these: two or more sentences in a row built as "X is a Y", such as "A retry is a replay. A replay is a duplicate."; a sentence whose subject is an abstract "One", such as "One lesson is".

FAIL when any of them appears. Name the pattern and quote the sentence.
