---
type: regex
pattern: "\\b(this|these) (document|note|notes|proposal|write-?up|update|report|postmortem) (argues|describes|explains|proposes|outlines|covers|summari[sz]es|decides)\\b"
flags: im
match: not_contains
target: last_message
weight: 1
---

The document named as the one who decided hides who decided (the pattern "the document as author").
