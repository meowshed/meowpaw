---
id: RES-0032
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Tests, and whether they prove anything

## Summary

Coverage is no evidence, and the measured position is worse for generated code.
Model-written tests score around twenty per cent on mutation testing for
complex functions, and mutants survive more often at equivalent coverage. So
every test is asked whether it would fail if its requirement were violated.
Weak assertions and tautologies are defects in the check and no gaps in
coverage, and a test names the requirement it proves.

Research for the testing obligations in `meow-flow` and `meow-review`, and for
the per-language testing knowledge in the packs. The harness requires every
requirement to be traceable to a check that would fail if the requirement were
violated. This is about whether that is true in practice.

## Method

The published material was fetched and read on 2026-09-20: the technology
radar entry for mutation testing as a fault-detection signal, and the studies
and guides reporting the figures for generated tests.

Those figures are secondary. They were not reproduced here, and are recorded as
reported with their sources named, which matters because they are the strongest
numbers in this document.

The internal repositories and the surveyed harnesses were read for what each
treats as proof, which is how the finding that one of ten checks test integrity
was reached. Nothing was run.

## The measurement that settles it

Mutation testing injects deliberate defects and reports which ones the tests
fail to catch. It is the only honest measure of a suite's fault-detection
ability, and applied to model-generated tests the numbers are bad:

- **LLM-generated tests score around 20% on mutation testing** for complex
  real-world functions. Roughly four in five injectable defects survive.
- **Mutant survival is 15-25% higher on AI-generated code at equivalent
  coverage.** The same coverage number, materially weaker tests.

Coverage is therefore not evidence. A suite can execute every line and assert
almost nothing, and a model optimising for coverage produces exactly that.

## The two anti-patterns, named

The literature converges on two, and both are recognisable on sight:

Weak assertions. `toBeDefined`, `is not None`, `len(x) > 0`, `assert result`

- checks that tolerate a wrong value. The most frequent defect in generated
  tests. It passes for any non-empty answer, including the wrong one.

Tautology. The test mocks the function it claims to test and asserts the
mock's return value. It cannot fail, and it reports coverage over the thing it
did not exercise.

`meowctl`'s review skill names the same failure from the other end: "A test that
asserts the code does what the code does is worse than no test, because it
reports coverage it does not provide."

## The question that catches both

> Would this test fail if its requirement were violated?

Asked per test, against the requirement, without running anything. It is
`meowctl`'s fourth verification step and it is described there as "the slow part
and the part that matters" ([RES-0063-verify.md](RES-0063-verify.md)).

A model is unusually well suited to answering it, because it requires reading
the assertion against the obligation, and executes nothing. And it is the
cheapest available defence against a suite that is green and hollow.

The stronger version, where the ecosystem has a tool: **mutate and see**.
Stryker, `mutmut`, PIT, `cargo-mutants`. That measures something, where the
other answer judges it, and a pack offers it where available as an occasional
check and never as a gate verb, because mutation runs are slow.

## Test-first, and why it is not a kernel rule

`superpowers` enforces test-first by **deleting code written before its test**.
The discipline is real, and it acts directly on assertion strength. A test
written against behaviour that does not exist yet cannot be a tautology,
because nothing exists to mock, and it cannot be weak, because it has to fail
first.

The harness rejects it as a universal rule ([design section 15]), because it is
false for a shader, a Compose file, a Godot scene and a Markdown document. A
rule that is wrong a third of the time is one people learn to bypass.

But the reasoning should be preserved where it applies: **red before green is
what makes an assertion strong**, and a pack for a language with a test runner
should say so. Test-first is a pack-level and profile-level choice that
somebody makes.

## What a requirement's check must be

From the rule that every requirement traces to a check that would fail, plus
the above:

- It **names the requirement** in a comment or a test name, so verification can
  find it mechanically. - It **asserts the obligation**, and never an adjacent
  fact. A requirement about an exit code is checked by the exit code, and the
  absence of an exception checks nothing. - It **would fail** if the
  requirement were violated - demonstrably, ideally by having been seen to fail
  once. - It covers the **failure path** the requirement specifies as well as
  the success path. This is where the internal survey found defects accumulate.

## The three kinds of check, and which to prefer

The harness's own conventions already name them: **static** (a script over the
repository), **behavioural** (a fixture with an assertion on files and exit
codes), and **eval** (a recorded conversation scored against the obligation).

The ordering is a preference and no taxonomy: prefer static to behavioural, and
behavioural to eval. An eval is the weakest - non-deterministic, expensive, and
scored by a model - and is used only where the obligation is genuinely about
what the model does with a prompt. A requirement that could have been static
and was made an eval instead is a finding.

## Conclusions

1. Coverage is not evidence. Never cite a coverage number as proof. 2. The
   question is whether the test would fail if the requirement were violated -
   asked per test, in review and in verification. 3. Weak assertions and
   tautologies are defects, named as such, and the test is rewritten, never
   supplemented. 4. A test names the requirement it proves. 5. The failure path
   is tested as precisely as the success path. 6. Red before green where the
   language supports it, as a pack-level rule. 7. Mutation testing where the
   ecosystem has it, as an occasional check. 8. Prefer static to behavioural to
   eval.

## Sources

- [Mutation testing](https://www.thoughtworks.com/radar/techniques/mutation-testing),
  Thoughtworks Technology Radar, read 2026-09-20 - mutation testing as the most
  honest signal of fault-detection capability.
- [Mutation testing for AI-generated code: a practical guide](https://www.augmentcode.com/guides/mutation-testing-ai-generated-code),
  read 2026-09-20 - **survival rates 15-25% higher on AI-generated code at
  equivalent coverage**.
- [Mutation-guided unit test generation with a large language model](https://arxiv.org/pdf/2506.02954),
  read 2026-09-20 - **LLM-generated tests at about 20.32% mutation score on
  complex real-world functions**.
- [When AI tests pass but your code still breaks](https://keelcode.dev/blog/ai-tests-safety-illusion),
  read 2026-09-20 - weak assertions and tautological mocking as the two
  commonest anti-patterns.
- [Reviewing AI-generated tests: a code-review checklist](https://qaskills.sh/blog/reviewing-ai-generated-tests-checklist-2026),
  read 2026-09-20.
- [TOGLL: correct and strong test oracle generation with LLMs](https://arxiv.org/pdf/2405.03786),
  read 2026-09-20 - oracle strength as distinct from oracle presence.
- [Mutation testing: the missing safety net for AI-generated code](https://dev.to/rsri/mutation-testing-the-missing-safety-net-for-ai-generated-code-54kn),
  read 2026-09-20 - "perpetually green" tests.
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness), read
  2026-09-20 - `test-integrity-guard.sh`, the only check for this found in the
  survey.
- `~/workspace/meowctl/.claude/commands/review.md`, read 2026-09-20 - "would
  this test fail if its requirement were violated" as the slow and load-bearing
  verification step.
