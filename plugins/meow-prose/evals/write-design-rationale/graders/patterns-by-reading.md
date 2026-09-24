---
type: llm
focus: last_message
weight: 2
---

Judge the text for the patterns that have no reliable marker.

PASS when the text has none of these: a contrast whose consequence is missing, such as "The fix is ownership, not tooling", appearing more than once; a long sentence followed by a short punchline under eight words; a sentence opening "That" or "This" that points at the whole previous sentence.

FAIL when any of them appears. Name the pattern and quote the sentence.
