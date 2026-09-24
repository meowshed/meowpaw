---
type: regex
pattern: "\\b(as (mentioned|noted|discussed) (above|earlier|before)|in the next section|this section (covers|describes|explains))\\b"
flags: im
match: not_contains
target: last_message
weight: 1
---

A sentence about the text costs the reader a sentence and gives nothing back (the pattern "text about the text").
