---
type: regex
pattern: "\\b(worth (noting|reading|mentioning|calling out)|matters (more|most)|the honest|honestly|key (takeaway|insight|point)|it is important|importantly)\\b"
flags: im
match: not_contains
target: last_message
weight: 1
---

A frame that promises importance delays the important thing (the pattern "importance promised instead of given").
