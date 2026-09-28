---
id: REQ-3183
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-09-28
elaborates: RES-0027
source: BUG-1230
verification: behavioural
---

# REQ-3183

Where the check REQ-3182 asks for blocks a text, it MUST quote the span that
breaks the rule, and the span MUST occur verbatim in the command as the
command is written, before the shell expands or unescapes it.

A span the author can find is a finding the author can fix or dispute. A
block naming a span that isn't there can only be retried, and BUG-1230 records
four such blocks on one day, each passing after a reword.
