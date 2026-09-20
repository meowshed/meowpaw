---
id: REQ-2948
artifact: requirement
topic: routing
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0261
verification: behavioural
---

# REQ-2948

The harness MUST distinguish an absent profile, an unparseable one and one
parsed with unknown keys, and MUST leave verbs unresolved rather than fall
back to detection when the profile cannot be parsed.

Falling back silently ignores what the repository tried to say.
