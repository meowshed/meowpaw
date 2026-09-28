---
id: REQ-3187
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-09-28
elaborates: RES-0027
source: BUG-1230, and the repository owner's decision
verification: judgement
---

# REQ-3187

A program MUST block a text for breaking the writing standard only on a rule
that names its defect as one of three things: a phrase from a closed list, a
construct of Markdown syntax, or an argument of the command that publishes the
text.

The standard is mostly about shape, and a pattern that reaches a paragraph
opening in bold or a claim written as a proverb has to guess at meaning, so it
trips on the wrong text and gets switched off. A rule of one of the three
kinds asks for no guess, and a program settles it the same way every time,
where a model asked to judge such rules named phrases the text didn't hold
(BUG-1230). RES-0027 puts the mechanical checks in the gate and the judgements
in review, and this states which rules count as mechanical for a program that
blocks. Any other rule, such as title case in a heading, which needs a guess
about which words are names, stays with review until a decision shows it fits
one of the three.
