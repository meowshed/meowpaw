---
id: REQ-4116
artifact: requirement
status: draft
cites: RES-0340
---

# The prose gate's two-judge call is a nested model call

Where the prose gate's Claude Code hook invokes a model to judge a span of
text, the Pi extension's `user_bash` handler makes a nested model call with
`ctx.modelRegistry.streamSimple()`, passing the judge prompt from
`fragments/judge.md` and the text to judge. The handler runs the judge twice
and blocks only where both judgements agree, preserving the two-judge
semantics.

Rationale: The two-judge pattern is load-bearing: it is what distinguishes a
programmatic block (fixed list, exit code) from a model judgement (idioms,
acronyms, bold-open). A nested model call preserves the pattern while giving
the extension access to structured output and session usage.
