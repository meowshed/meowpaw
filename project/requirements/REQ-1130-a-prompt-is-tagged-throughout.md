---
id: REQ-1130
artifact: requirement
topic: prompt-format
class: functional
status: approved
revised: 2026-09-22
elaborates: RES-0270
verification: static
---

# REQ-1130

A prompt the harness ships MUST mark its parts with XML tags throughout, and
MUST NOT use Markdown headings as its skeleton.

A prompt's formatting carries into the reply it produces, so a skill whose
rules sit under headings teaches headings, and the harness asks for prose.
Tags also close, where a heading does not, so the end of each part is
unambiguous.
