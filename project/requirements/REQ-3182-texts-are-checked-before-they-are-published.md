---
id: REQ-3182
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-09-21
elaborates: RES-0027
verification: behavioural
---

# REQ-3182

The harness MUST check every text it produces against the writing standard
before publishing it, and MUST report what it found rather than publishing.

Publishing covers all of it: a commit, an issue, a pull request body, a review
comment, a release note. A defect found afterwards costs a record, an issue and
a change to correct it, where the same defect found first costs one edit. The
harness already checks its own commit message this way (REQ-1314), and the
texts around that message are most of what it writes.
