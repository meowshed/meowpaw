---
id: RES-0053
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:discover`

## Summary

A harness that demands nine steps for a typo is worked around, and a
worked-around harness reports process it did not perform. So classification
happens before any work, on the request and the repository, and never on
keywords, and reports the class and the reason. The route carries size and
shape, including the outcome that this is several separate changes; ambiguity
resolves upward and says so; a one-word override is accepted in either
direction; and the command writes nothing.

Classifies a request before any work starts, reports the class and the reason,
and accepts a one-word override.

## Who has an equivalent

| Harness        | Mechanism                                                  | Classes                                                                                    |
| -------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| harness4claude | A `UserPromptSubmit` hook, keyword-based                   | L0 bypass, L1 light, L2 full                                                               |
| cc-sdd         | `/kiro-discovery <idea>`                                   | Five _routes_: extend an existing spec, implement directly, one spec, several specs, mixed |
| meowhub        | Prose in its rules                                         | "trivial changes (typo, formatting, revert)"                                               |
| spec-workflow  | A separate command family                                  | Feature path, bug path                                                                     |
| spec-kit       | `assess-*` chain ending in go / needs-clarification / kill | A verdict, not a size                                                                      |

Nobody else has one.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## Two axes

The survey conflates them and they are independent:

- **Size** - how much method this change deserves. harness4claude's L0/L1/L2.
- **Shape** - what kind of work this is. cc-sdd's five routes; the bug path.

A request can be a small bug, a large bug, a small feature that extends an
existing specification, or three unrelated things pretending to be one. A
classifier with only a size axis will try to run one chain over the last case.

So the output is a route, and no label: _this is L1 defect work against unit
0007_, or _this is three units, and here they are_.

## Keyword or judgement

harness4claude classifies on bilingual keyword analysis at a hook. Cheap,
deterministic, and wrong the moment someone describes an architectural change
in plain words.

A model reading the request _and the repository_ classifies better and is
non-deterministic. That trade is acceptable only with two things attached, and
they are why classifying before work starts, and the one-word override, exist:
the class and the reason are reported, and never applied silently, and a person
overrules in one word.

## The asymmetry

Mis-routing down is a defect - an architectural change made as a typo fix, with
no requirement and no record. Mis-routing up wastes an hour.

That is not a close call, so ambiguity resolves upward and the harness says it
did. The failure this guards against is the one that looks like
helpfulness: the model that "just fixes it" because the request sounded small.

## Writing nothing

`discover` produces a decision and no artifact. It is the one step in the whole
surface with no file, which is deliberate: a classifier that writes a document
has made the trivial path non-trivial and defeated its own purpose.

## Conclusions

1. Classify on the request **and** the repository, and never on keywords. 2.
   Report the class and the reason before work starts. 3. Output a route - size
   _and_ shape - including "this is several changes". 4. Resolve ambiguity
   upward and say so. 5. Accept a one-word override in either direction. 6.
   Start defect work at reproduction. 7. Write nothing.

## Sources

All read 2026-09-20.

- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) - L0/L1/L2
  classification at the `UserPromptSubmit` hook, by bilingual keyword analysis.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - `/kiro-discovery` and
  its five routes, including implement-directly and mixed decomposition.
- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow)
  - the separate bug path as a second axis.
- [github/spec-kit](https://github.com/github/spec-kit) - the assessment chain
  ending in go / needs-clarification / kill.
- `~/workspace/meowhub/CLAUDE.md` - the trivial-change exception in prose.
