---
id: RES-0254
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0028, RES-0253
---

# The requirement template

## Summary

The standard defines eleven attributes and this corpus carries eight. Three of
the omissions are right for one shared reason: priority, owner and difficulty
describe scheduling and never what must be true. The fourth omission is not. No
requirement carries a rationale, although this project's own finding is that a
rule without its reason is applied literally and wrongly

- a finding it applied to skills, commits and the constitution and never to its
  most numerous rules.

Research for the shape of a requirement: which attributes it carries, what its
text looks like, and which of the standard's attributes this corpus dropped
without deciding to.

One of nine template documents, one per artifact kind in the record.

It does not cover how requirements are written, which is
[RES-0028-requirements.md](RES-0028-requirements.md), nor the command that
produces them, which is
[RES-0151-requirements-command.md](RES-0151-requirements-command.md).

## The question

Six hundred and eighty-six requirements in this corpus carry eight front-matter
fields. The standard this project took its quality criteria from defines
eleven attributes, and the overlap is partial.

So the question is which of the missing three matter, and the answer turns out
to include the one the project's own findings say matters most.

## Method

The standard's attribute set was taken from the vendor documentation that
lists it, fetched on 2026-09-20; the standard itself was not obtained, which is
the same limitation the requirements research already records.

This corpus was read against it: the front matter of the requirements was
compared field by field with the attribute list, which is how we identified the
four omissions, recalling none of them.

The counts of requirements that failed the single-obligation and prohibition
rules come from the earlier corrections recorded in this corpus, and from no
fresh count.

## Findings

### The standard's attribute set, against this corpus's

The requirements-engineering standard defines these attributes for a
requirement: **Id, Heading, Text, Owner, Priority, Source, Rationale,
Difficulty, Type, Status, Verification Method.**

This corpus carries: identifier, artifact kind, topic, class, status, revision
date, what it elaborates, and verification method.

| Standard attribute  | Here                                                                            |
| ------------------- | ------------------------------------------------------------------------------- |
| Id                  | Yes, as the identifier                                                          |
| Heading             | Yes, as the slug and title                                                      |
| Text                | Yes                                                                             |
| Type                | Yes, as the class                                                               |
| Status              | Yes                                                                             |
| Verification Method | Yes                                                                             |
| Source              | Partly - `elaborates` names the research, not the person or document that asked |
| **Rationale**       | **No**                                                                          |
| Priority            | No                                                                              |
| Owner               | No                                                                              |
| Difficulty          | No                                                                              |

Three of those omissions are defensible and one is not.

### The missing rationale contradicts one of this project's own central findings

The synthesis records, as finding ten, that **a rule without its reason gets
applied wrongly**. A rule whose reason is stated survives contact with a case
its author never foresaw, because the reader can tell whether the reason
applies. A rule without one is followed literally and wrongly.

That finding was applied to skills, to the constitution and to commit messages.
It was not applied to requirements, which are the most numerous rules in the
corpus and the ones most often read by someone who was not there.

The `elaborates` field is not a substitute. It names the research document a
requirement came from - frequently a document of two hundred lines with a dozen
conclusions - which tells a reader where to look and never why the requirement
exists. Following it costs a document read; a rationale costs a sentence.

The counter-argument is real and should be recorded: a rationale on six hundred
requirements is six hundred sentences that must be maintained, and a stale
rationale is worse than none. The resolution is that **a rationale is written
where the obligation would otherwise look arbitrary**, and omitted where the
requirement states its own reason. A requirement saying an unresolved verb is
reported and never guessed at carries its reason in its text; one fixing a
number, a format or a choice between two acceptable options does not.

### Priority, owner and difficulty are correctly absent, and for one shared reason

All three are project-management attributes: they describe how work on a
requirement will be scheduled and by whom, and never what must be true.

This corpus separates those deliberately. What must be true is a requirement;
what will be done about it is an epic and its tasks; who does it is the forge's
business. Carrying priority on a requirement would put a scheduling decision in
the artifact the method keeps free of them, and it would go stale immediately,
because priority changes without the requirement changing.

Difficulty is worse: it is an estimate about an implementation that has not
been designed, recorded against a statement that is supposed to outlive several
implementations.

So the omissions are right, and the reason is written down, so nobody reads
them as an accident.

### Source and elaborates answer different questions, and only one is recorded

The standard's `Source` is where the requirement came from: a stakeholder, a
regulation, a prior document. This corpus's `elaborates` is where it was
derived from inside the corpus.

For a project whose requirements are derived from its own research the two
nearly coincide, which is why the gap has not hurt. It will hurt as soon as a
requirement comes from outside: a licence obligation, a platform limit, a
user's explicit instruction. The corpus then records the research that noticed
it, and never the thing that imposed it.

The user instruction case is already live here: several requirements in this
corpus exist because a person said so, and the record shows a research document
as their origin.

### The text is one obligation, stands alone, and uses the keyword correctly

Three properties, all already established, and the template restates all three
because they are the ones a generated requirement fails.

One obligation. A requirement with two `MUST` clauses cannot be cited by
one check and cannot be withdrawn in half.

Stands alone. A requirement that says _that command_ or _such a record_
breaks when its neighbour moves. Sixteen here were written that way and had to
be rewritten.

A prohibition is `MUST NOT`. _No X MUST Y_ negates a requirement rather
than prohibiting a behaviour. Twelve here were written the first way.

Each of those is mechanically checkable and only the first is checked today.

### Verification method is a declaration, and its vocabulary is now four values

Every requirement declares how it is verified. The vocabulary is a static
check, a behavioural fixture, a recorded evaluation, or a declared judgement.
The fourth arrived when the corpus found that several requirements demanded
judgements no verb could make, while none declared itself verified that way.

The template rule that follows: **a requirement declaring judgement names who
judges**, an agent or a person. The two see different things, and the corpus
reports how much of itself rests on each.

### The sections it carries

| Field          | Holds                                            | Mandatory        |
| -------------- | ------------------------------------------------ | ---------------- |
| `id`           | The permanent identifier                         | Yes              |
| `artifact`     | The kind                                         | Yes              |
| `topic`        | The block it belongs to                          | Yes              |
| `class`        | Functional or a named quality attribute          | Yes              |
| `status`       | Stored status only                               | Yes              |
| `revised`      | When a person last changed it                    | Yes              |
| `elaborates`   | The research it was derived from, many to many   | Yes              |
| `source`       | What imposed it, where that is not the research  | Where applicable |
| `verification` | Check, fixture, evaluation or judgement          | Yes              |
| `verifier`     | Agent or person, where verification is judgement | Where applicable |

Body: one sentence carrying one obligation, standing alone, with the keyword
used correctly; then, where the obligation would otherwise look arbitrary, one
sentence of rationale.

## Conclusions

1. A requirement carries a rationale where the obligation would otherwise look
   arbitrary, because this project's own finding is that a rule without its
   reason is applied literally and wrongly. 2. A rationale is omitted where the
   text already carries its reason, so the corpus does not maintain six hundred
   sentences that repeat their requirements. 3. `elaborates` is not a
   rationale. It names a document to read; a rationale costs a sentence and
   answers the question directly. 4. A requirement imposed from outside records
   what imposed it, separately from the research that noticed it, including
   where the imposer is a person's instruction. 5. Priority, owner and
   difficulty are deliberately absent, because they describe scheduling and
   never what must be true, and each would go stale without the requirement
   changing. 6. The text carries exactly one obligation, so one check can cite
   it and it can be withdrawn whole. 7. The text stands alone, naming its own
   subject and referring to no neighbour. 8. A prohibition is written `MUST
NOT`, never as a negated requirement. 9. The single-obligation,
   standing-alone and prohibition-form rules are checked mechanically, since
   all three are checkable and only one is checked today. 10. Verification
   declares one of four methods, and where it declares judgement it names
   whether an agent or a person judges. 11. Only the stored status is in the
   front matter, and whether the requirement is satisfied is derived, and
   recorded nowhere.

## Sources

All read 2026-09-20.

- [ISO/IEC/IEEE 29148 requirements specification templates](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)
  - the standard's requirement attributes: Id, Heading, Text, Owner, Priority,
    Source, Rationale, Difficulty, Type, Status and Verification Method; and the
    document families the standard defines.
- [RES-0028-requirements.md](RES-0028-requirements.md) - the quality criteria
  this corpus adopted from the same standard, and the notations compared.
- [RES-0001-synthesis.md](RES-0001-synthesis.md) - finding ten, that a rule
  without its reason gets applied wrongly and that a stated reason survives a
  case its author did not foresee.
- [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - the four verifiers,
  the fourth verification value, and the finding that the corpus declared no
  requirement verified by judgement while requiring judgements.
- [RES-0151-requirements-command.md](RES-0151-requirements-command.md) - the
  single-obligation, standing-alone and prohibition-form rules, and the counts
  of requirements in this corpus that failed each.
- This corpus, read 2026-09-20: the front matter of the requirements in
  `project/requirements/`, compared field by field against the standard's
  attribute set.
