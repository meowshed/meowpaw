---
type: llm
focus: last_message
weight: 2
---

Judge the text for the patterns that have no reliable marker.

PASS when the text has none of these: a sentence opening "That" or "This" that points at the whole previous sentence, such as "This means we are on track"; a bare pointer fragment such as "See the ticket." ending a paragraph.

FAIL when any of them appears. Name the pattern and quote the sentence.
