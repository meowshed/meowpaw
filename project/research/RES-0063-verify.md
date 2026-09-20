---
id: RES-0063
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:verify`

## Summary

Verification reports how the work and its artifacts disagree, in every
direction, and changes nothing but the status it is the act of moving. It
reports all four directions worst-first, judges whether each check would
actually fail if its requirement were violated, reports a clean result in one
sentence without padding, and offers remediation, applying none of it.

Reports how the work and its artifacts disagree, in every direction, and
changes nothing.

## Who has an equivalent

| Harness        | Command                                    | Read-only                                                                                                        |
| -------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| spec-kit       | `speckit-analyze`                          | Yes, with an opt-in remediation offer                                                                            |
| meowctl        | `/verify`                                  | Yes, explicitly: "it reports; deciding whether the code or the spec is wrong is a judgement someone has to make" |
| harness4claude | `verify-against-spec`, `verify-multimodel` | Produces evidence                                                                                                |
| cc-sdd         | `kiro-validate-gap`                        | Optional gap analysis                                                                                            |

Two harnesses independently decided the analysis command must not modify
anything. That is the strongest support available for a verification step that
changes nothing, and the reason
is the same in both: a command that both detects and resolves divergence will
always resolve it by rewording the specification.

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

## What spec-kit's `analyze` checks

Six categories, and they are a better enumeration than ours had:

1. Duplication - near-identical requirements.
2. Ambiguity - vague attributes (fast, secure) with no measurable threshold;
   unresolved placeholders.
3. Underspecification - missing outcomes, acceptance criteria, components.
4. Constitution conflicts - violations of a MUST principle.
5. Coverage gaps - requirements with no task, tasks with no requirement.
6. Inconsistency - terminology drift, entity misalignment, contradictory
   ordering.

With a four-level severity model where CRITICAL is a constitution violation, a
missing core artifact, or a zero-coverage requirement blocking baseline
functionality.

## The four directions ours must report

Ours checks more than coverage, because our artifacts carry status:

1. Specified and unchecked: a requirement no check names. 2. Checked and
   unspecified: a check citing an identifier that does not exist: either a
   withdrawn requirement whose check survived, or a typo. 3. Built and
   unspecified: observable behaviour no requirement covers. 4. Recorded state
   against actual state - tasks marked done with no evidence, work landed
   against an unticked task, a requirement whose status disagrees with its
   coverage, front matter contradicting where the work sits. And the plan
   against the tracker.

The fourth is ours alone. Nothing in the survey checks whether the documents
still describe the tree.

## The part that is slow and matters

meowctl's fourth step: "An ID in a doc comment proves somebody typed the ID, not
that the test checks the obligation. For each one, say whether the test would
actually fail if the requirement were violated. This is the slow part and it is
the part that matters."

A model is unusually well suited to this, because it requires reading the check
against the requirement, and runs nothing.

## The remediation offer

spec-kit ends with a non-destructive offer: concrete edit suggestions the user
opts into. That preserves read-only while being useful, and is better than
either extreme.

## Conclusions

1. Write no artifact. Moving the status of the task and its epic is the act of
   verifying and is the only thing it leaves behind.
2. Report all four directions, worst first.
3. Judge whether each check would actually fail if its requirement were
   violated.
4. Report a clean result as clean, in one sentence, without padding.
5. Offer remediation, never apply it.

## Sources

All read 2026-09-20.

- [github/spec-kit `analyze.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/analyze.md)
  - read-only cross-artifact analysis, the six defect categories, the four-level
    severity model, the coverage summary, and the non-destructive remediation
    offer.
- `~/workspace/meowctl/.claude/commands/verify.md` - bidirectional checking,
  tombstones distinguished from typos, and "would the test fail if the
  requirement were violated" as the slow and load-bearing step.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) -
  `verify-against-spec` item-by-item coverage, and multi-model verification.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - `kiro-validate-gap`.
