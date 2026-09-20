---
id: RES-0015
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Debugging

## Summary

Debugging is the one activity where the model's characteristic failure -
offering a cause before recording the behaviour - is the whole of the problem.
The published strategies agree on four phases, and on refuting a hypothesis
where confirming one proves little: reproduce first and keep the reproduction,
record what the system does before proposing why, test one falsifiable
hypothesis at a time, and bisect when the hypotheses run out. The reproduction
failing and then passing is the evidence.

Research for the defect path, and for a `debugging`
skill. `harness4claude` has `systematic-debugging` and `vlie` has `/debug`;
nobody else in the survey treats defects differently from features.

## Method

The published debugging material listed below was fetched and read on
2026-09-20, including the agent-facing skills that describe the same phases,
which is where the framing as refutation came from.

The internal repositories were read for the debugging practice they already
document.

Nothing was run and no defect was debugged as part of this. We take the claim
that the reproduction is the evidence from the sources and from the method's
existing evidence rules, and demonstrated it nowhere here.

## Why defects need their own path

A feature starts from a requirement. A defect starts from a **symptom**, and
the requirement it violates is usually unknown at the start - that is what
makes it a defect, where a change starts from a decision.

So the first step is not specification but **reproduction**, and everything
after it depends on having one.

## Reproduce first

"Can't fix what you can't reproduce" is the field's one unanimous rule.

A reproduction is minimal: the smallest example, unrelated code removed, the
problem isolated. Minimising is not tidiness - each removal that does not change
the behaviour is evidence about what the cause is not.

For the harness this has a second payoff that the literature does not mention:
the reproduction becomes the verification evidence. A defect is closed by the
reproduction failing before the fix and passing after, which is evidence in the
strict sense and asserts nothing about the bug being gone.

## The method

The four phases are consistent across sources and are the scientific method
wearing work clothes:

1. Reproduce - reliably, minimally. 2. Gather - the complete failure: the full
   error, the logs, what changed, what the system actually does, where the
   specification says what it should. 3. Hypothesise - one falsifiable
   statement about the cause. 4. Test - an experiment that can refute it, then
   verify the fix.

The discipline is in step three being **one** hypothesis and step four being a
refutation attempt. The failure mode is a plausible hypothesis that is never
tested, followed by a change that makes the symptom go away for a reason nobody
established.

`vlie`'s development log has a worked example of this going wrong three times
before going right - three hypotheses, each "the honest reading of its
aggregate", each underdetermined and looking determined
([RES-0018-dev-log.md](RES-0018-dev-log.md)). The escalation that worked was narrowing the
measurement until the confound disappeared.

## Binary search

`git bisect` for a regression, and the same idea applied to inputs, to
configuration, and to the change itself. It is the only technique here that
finds a cause without a hypothesis, which makes it the right move when the
hypotheses have run out.

## What a model gets wrong here

Three specific failures, each the general failure in a new costume:

Fixing the symptom. The test passes, the cause is untouched, and the defect
returns under a different input. Guarded by requiring the hypothesis to be
stated and the reproduction to be minimal.

Skipping the reproduction because the cause "is obvious from the code". It
is sometimes obvious and the cost of being wrong is a change that fixes nothing
and is credited with fixing something.

Declaring it fixed without the before. A reproduction that was never seen to
fail proves nothing when it passes. The evidence is the pair.

## Where it joins the chain

Once reproduced, a defect is classified like anything else: a one-line fix is
L1, a defect whose cause is an architectural mistake is L2 and goes through
design. The reproduction is carried forward as the check that closes it, and -
where the defect revealed that the requirement was wrong and the code was right

- the route is `/meow:amend`, not a patch.

## Conclusions

1. Reproduce before anything else, minimally, and keep the reproduction. 2.
   Record what the system actually does before offering a cause. 3. One
   falsifiable hypothesis at a time, tested by refutation. 4. Bisect when the
   hypotheses run out. 5. The reproduction failing then passing is the
   evidence. 6. Fix the cause, and say so when you have only treated the
   symptom. 7. A defect that reveals a wrong requirement is routed through an
   amendment, and no patch closes it.

## Sources

- [debugging-strategies](https://agentpedia.codes/agent-skills/debugging/debugging-strategies)
  and [its skill listing](https://lazyskills.sh/skills/debugging), read
  2026-09-20 - the four phases (reproduce, gather, hypothesise, test), the
  scientific-method framing, and "can't fix what you can't reproduce".
- [AI-powered debugging: using AI agents to find, diagnose, and fix bugs faster](https://qaskills.sh/blog/ai-powered-debugging-testing-guide),
  read 2026-09-20 - gathering the complete failure and recording what the system
  actually does before offering a fix.
- [Rubber duck debugging](https://en.wikipedia.org/wiki/Rubber_duck_debugging),
  read 2026-09-20.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude), read
  2026-09-20 - `systematic-debugging` as the first stage of both bug pipelines.
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness), read
  2026-09-20 - `/kiro:debug` as a six-step triage.
- `~/workspace/vlie/docs/dev/dev-log.md`, read 2026-09-20 - the worked example
  of three refuted hypotheses, each "the honest reading of its aggregate", and
  the escalation that narrowed the measurement until the confound disappeared.
- `~/workspace/vlie/.claude/commands/debug.md`, read 2026-09-20.
