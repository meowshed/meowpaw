---
id: REQ-1132
artifact: requirement
topic: prompt-format
class: functional
status: draft
revised: 2026-09-22
elaborates: RES-0270
verification: behavioural
---

# REQ-1132

Text from outside the harness that a prompt carries, such as a text under
review, a pasted document or a tool's output, MUST sit inside tags that mark it
as outside text, with the prompt stating that instructions inside them are
data. Where the harness assembles the prompt itself, the opening and closing
tags MUST carry the same identifier, generated for that call.

A reviewer reading a commit message that says "ignore your criteria" should
read it as a commit message. A fixed tag can be closed by the text inside it,
and a random identifier cannot be guessed in advance.
