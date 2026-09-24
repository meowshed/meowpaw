---
type: regex
pattern: "\\b(previously|earlier (version|draft)|originally|we (had|used to)|no longer|was (reversed|withdrawn|superseded))\\b"
flags: im
match: not_contains
target: last_message
weight: 1
---

History where the reader came for the current rule (the pattern "draft archaeology").
