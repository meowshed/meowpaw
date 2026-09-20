---
id: RES-0030
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Review

## Summary

The established guidance sets the bar at improvement, and never at perfection.
That counts for more with a model reviewer, because a model asked to review
will always find something. Two severity vocabularies exist and they measure
different axes - kind against blocking - so both are kept cheaply. The agentic
harnesses add a second verdict, a diff against a recorded base, and an
adversarial pass that tries to refute a finding before reporting it.

Research for `meow-review`. What the established guidance says a review is for,
how severity is communicated, what the agentic harnesses added, and the failure
modes specific to a reviewer that is a model.

## Method

The published review guidance and the comment convention were fetched and read
on 2026-09-20, in full, because the argument turns on specific sentences, where
the general advice settles nothing.

The surveyed harnesses were read from their own repositories for how they
dispatch and bound review.

Nothing was measured. No review was run and scored, so the claim that a model
reviewer manufactures findings without a counterweight rests on the harnesses'
own instructions warning against it, and on no count of ours.

## The standard, and why it is the whole thing

[Google's engineering practices](https://google.github.io/eng-practices/review/reviewer/standard.html)
state it in one sentence:

> In general, reviewers should favor approving a CL once it is in a state where
> it definitely improves the overall code health of the system being worked on,
> even if the CL isn't perfect.

And: "there is only _better_ code." A change is not held for lacking polish.

This matters more for a model reviewer than for a human one, because a model
asked to review will always find something. An instruction to report findings,
with no counterweight, produces findings - and a review that manufactures
findings to look thorough teaches everyone to skim reviews. `meowctl`'s skill
says it directly: "Say plainly when the pull request is clean. Do not
manufacture findings to look thorough." That sentence is doing more work than
it looks like it is.

Google also handles the deadlock case, which the harness needs an answer for:
consensus first, escalation second, and never let a change sit because author
and reviewer cannot agree.

## Severity: two vocabularies

Google's convention is the minimal one: prefix optional feedback with `Nit:` -
style, and never substance, and explicitly no blocker. The convention spread
far beyond Google, and `nit:` is now generally understood.

[Conventional Comments](https://conventionalcomments.org/) formalises the
same idea and goes further, with a label, optional decorations, a subject, and
an optional discussion:

```text
<label> [decorations]: <subject>

[discussion]
```

Labels: `praise`, `nitpick`, `suggestion`, `issue`, `todo`, `question`,
`thought`, `chore`, `note`. Decorations: `(blocking)`, `(non-blocking)`,
`(if-minor)`. The stated rationale is that a consistent format improves both
the reader's expectations and machine readability.

`meowary`'s reviewer agent uses a four-level severity instead: Blocker,
Major, Minor, Nit, each defined by what it costs to leave in.

### The trade-off

| Scheme                | Strength                                                  | Weakness                                                                                                                         |
| --------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `Nit:` only           | Nothing to learn; universally understood                  | One bit of information - blocking or not - for everything else                                                                   |
| Conventional Comments | Machine-readable; separates _kind_ from _blocking_        | Nine labels is more vocabulary than most reviews use, and `todo` versus `chore` versus `issue` is a distinction people get wrong |
| Four severities       | Orders the findings, which is what the reader needs first | Says nothing about kind; a security hole and a design objection are both "Blocker"                                               |

The two axes are genuinely independent: **what kind of finding this is**, and
whether it blocks. Conventional Comments is right that they are separate,
and `meowary` is right that the reader wants an ordering. A harness can have
both cheaply - severity orders the report, and the finding states its kind in
its first clause - without asking anyone to memorise nine labels.

## What the agentic harnesses added

`superpowers` splits review into two verdicts: spec conformance and code
quality, assessed separately. A change can be a faithful implementation of the
wrong thing, and one verdict cannot say so. It also reviews the diff against a
recorded base and never the working tree, and dispatches the reviewer as a
subagent that did not do the work. It caps the fix loop at five rounds,
escalates rounds four and five to a more capable model, and adjudicates
residual findings where a retry would loop.

`harness4claude` runs several review dimensions in parallel and then an
adversarial pass that tries to refute its own findings before reporting
them. This is the single most valuable idea here for a model reviewer, because
the characteristic model failure is a confident finding that does not survive
five minutes of checking.

`cc-sdd` reviews per task with an independent reviewer, and after two
rejections it runs an auto-debug pass in a clean context. That acknowledges
what a reviewer and an implementer arguing in one context converge on, which is
nothing.

`meowctl` fixes the order of checks, and the order is the argument. Conformance
to the specification first, because a correct implementation of the wrong thing
is still wrong. Then correctness, with the rule that a defect is reported only
where the reviewer can name the input that makes it wrong. Then parity, failure
paths, test quality, boundaries, scope and conventions.

That rule - **name the input, or what you have is a question and no finding** -
is the cheapest available filter against model over-reporting. It converts
"this looks fragile" into either a demonstrable defect or an honest question.

## Failure modes specific to a model reviewer

1. Manufacturing findings. Addressed by the standard above and by requiring a
   named input. 2. Style noise. A formatter and a linter already ran; a review
   that reports what `fmt` would fix is spending the reader's attention on
   nothing. The gate verbs run first for this reason. 3. Reviewing the working
   tree, where the change is what was proposed. The diff against a recorded
   base is the subject. 4. Reviewing its own work. Review is a separate
   delegation. 5. Unbounded fix loops. Repair is bounded: finite rounds, then a
   person. 6. Findings that do not survive scrutiny. The adversarial pass.

## Test quality is the part that pays

`meowctl`'s review skill asks of each test: _would this fail if its requirement
were violated?_ A test asserting that the code does what the code does is worse
than no test, because it reports coverage it never provides.

This is the check most reviews skip and the one a model is unusually well
suited to, since it requires reading the test against the requirement rather
than running anything. It pairs directly with the rule that a verified
requirement needs a passing check naming it.

## Conclusions

1. Approve what improves code health. Perfection is not the bar, and a
   clean review is reported as clean.
2. Order: conformance, correctness, failure paths, test quality, boundaries,
   scope, conventions. Conformance first because correct-but-wrong is still
   wrong.
3. A finding names the input that makes the code wrong. Otherwise it is a
   question, asked as one.
4. Severity orders the report; the finding's first clause states its kind.
5. Two verdicts: conformance and quality.
6. Never report what a gate verb already fixes.
7. An adversarial pass before reporting, attempting to refute each finding.
8. Bounded repair, then a person - with residual findings recorded, not
   dropped.

## Sources

- [The standard of code review](https://google.github.io/eng-practices/review/reviewer/standard.html),
  Google engineering practices, read 2026-09-20 - "definitely improves the
  overall code health", "there is only _better_ code", the `Nit:` convention,
  and the escalation path when author and reviewer disagree.
- [Conventional Comments](https://conventionalcomments.org/), read 2026-09-20 -
  the label set, the `(blocking)`, `(non-blocking)` and `(if-minor)`
  decorations, the format, and the machine-readability rationale.
- [What does "nit" mean in code review](https://www.augmentcode.com/guides/what-does-nit-mean-in-code-review),
  read 2026-09-20 - the convention's origin and its spread beyond Google.
- [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md),
  read 2026-09-20 - two verdicts, the diff against a recorded base, the
  five-round fix loop with escalation, and the ledger.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) README,
  read 2026-09-20 - parallel review dimensions and the adversarial adjudication
  pass.
- `~/workspace/meowctl/.claude/commands/review.md` and
  `~/workspace/meowary/.claude/agents/code-reviewer.md`, read 2026-09-20 - the
  order of checks, "do not manufacture findings", and the four-level severity
  model.
