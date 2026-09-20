---
id: RES-0214
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0017, RES-0201
---

# The `threat-model` skill

## Summary

Tests written without a threat model are mechanical, because they assert
whatever the policy happens to say - which is the sharpest argument for the
lens. Adversaries are ordered by likelihood of causing damage rather than by
severity, and the most probable one is accident by a legitimate insider, which
calls for different protections than a model aimed at attackers. Applied here,
the harness's own most probable adversary is itself, acting on a repository it
has just met.

Research for one design lens: what is protected, and who from, ordered by
likelihood of causing damage.

Its siblings are the other four lenses, listed in
[RES-0017-design-lenses.md](RES-0017-design-lenses.md).

## The question

The donor standard opens with the reason it exists: _"Tests written without a
threat model are mechanical, because they assert whatever the policy happens to
say."_

That is sharper than most security guidance and is the argument for the lens.
Without a statement of what is protected and from whom, a security test
verifies the implementation against itself, and every such test passes.

## Method

The donor standard was read in full from its working tree on 2026-09-20 and
quoted directly, including its opening argument and its scale rule.

The published threat-modelling process was fetched and read for the checklist
the donor material deliberately lacks: the four steps, the six categories and
the control each maps to, the trust-boundary definition, and the qualitative
ranking.

The harness's own asset list was derived from this project's other research
rather than from either source. Nothing was tested or attacked.

## Findings

### The structure is two lists

What is protected: the asset, why it matters, and the worst case if it is
lost.

Who you defend against, ordered by likelihood of causing damage.

Ordering by likelihood rather than by severity is the choice that makes the
document useful. A model ordered by severity opens with the catastrophic and
improbable, and the design that follows spends its effort there.

### The most probable adversary is accident by a legitimate insider

A stray tap, a bulk approval read too quickly, a deletion meant for something
else. The donor material lists it first and designs most of the system around
it.

A threat model that opens with external attackers is usually inventorying
imaginary adversaries, which produces - in the standard's own phrase - _"a
document nobody reads"_.

This is the most transferable finding in the lens, and it changes what the
design does. Protection against accident is undo, confirmation of inferred
decisions, and bounded blast radius, and a model aimed at attackers produces
none of those.

### A published taxonomy gives the checklist the donor material lacks

The donor standard is short by design and gives no enumeration. STRIDE
supplies one, and the six categories each map to a control:

| Threat                 | Control         |
| ---------------------- | --------------- |
| Spoofing               | Authentication  |
| Tampering              | Integrity       |
| Repudiation            | Non-repudiation |
| Information disclosure | Confidentiality |
| Denial of service      | Availability    |
| Elevation of privilege | Authorisation   |

The surrounding process is four steps. Scope the work through diagrams, entry
and exit points, assets and trust levels. Determine threats, then determine
countermeasures. Assess the work by checking that the diagrams, the threat list
and the control list exist.

Two concepts from it transfer whole. A **trust boundary** is _"the change of
trust levels as the data flows through the application"_, which is where the
interesting threats live. And threats are ranked qualitatively as high, medium
or low. The likelihood factors are remote exploitability, authentication
required and automatable. The impact factors are what is compromised, whether
administrative access follows, and how sensitive the data is.

The qualitative ranking is deliberate: it prevents the false precision of a
numeric score that nobody can defend.

### The scale rule, stated explicitly

A three-person household is not an enterprise, and the model is kept short on
purpose.

That belongs in the skill because the failure mode of adopting a published
taxonomy is producing an enterprise document for a project that has one user
and one machine. The taxonomy is a checklist to think against, not a template
to fill in.

### What this harness is protecting, which is unusual

This lens applied to the harness itself produces a short and specific list, and
this document records it because the assets are not the usual ones.

The repository's **secret material**, which the harness never reads, prints or
transmits. Several of its own tools would otherwise carry it off: a repository
packer, a search index, an environment file loaded by a task runner.

The **user's environment**, which is what a trust decision authorises access to

- the reason the harness grants trust for neither of the two runners that ask
  for it.

The **record's integrity**, since a corpus whose history can be rewritten
without trace is a corpus whose evidence means nothing. That is what commit
signing protects, and why a gate tests for a good signature exactly rather than
for the absence of a bad one.

And the most probable adversary here is the same as everywhere: accident by a
legitimate insider, which in this setting means the harness itself acting on a
repository it has just met.

## Conclusions

1. A design states what is protected, why it matters, and the worst case,
   or its security tests assert the implementation against itself.
2. Adversaries are ordered by likelihood of causing damage, not by
   severity, so the design spends its effort where the damage comes from.
3. Accident by a legitimate insider is considered first, because it is the
   most probable adversary and the protections it calls for are different.
4. A model that opens with external attackers is inventorying imaginary
   adversaries and produces a document nobody reads.
5. A published taxonomy is used as a checklist, with each category mapped
   to the control that answers it.
6. Trust boundaries are identified, since a change of trust level as data
   flows is where the interesting threats are.
7. Threats are ranked qualitatively, from likelihood and impact factors,
   because a numeric score is false precision.
8. The model is kept short and matched to the scale of the system.
9. The harness's own assets are named: the repository's secret material,
   the user's environment, and the integrity of the record.
10. The harness treats itself as the probable accident, since it acts on
    repositories it has just met.

## Sources

All read 2026-09-20.

- `~/workspace/meowhub/docs/standards/threat-model.md` - that tests written
  without a threat model are mechanical because they assert whatever the policy
  says; the two-list structure of what is protected and who you defend against;
  ordering by likelihood of causing damage; accident by a legitimate insider as
  the most probable adversary; the warning that a model opening with external
  attackers produces a document nobody reads; and the explicit scale rule.
- [OWASP threat modelling process](https://community.owasp.org/Threat_Modeling_Process)
  - the four steps of scoping, determining threats, determining countermeasures
    and assessing the work; the six STRIDE categories and the control each maps
    to; a trust boundary as the change of trust levels as data flows through the
    application; data flow diagrams with external entities, processes, data
    stores and privilege boundaries; and qualitative high, medium and low ranking
    from likelihood and impact factors.
- [RES-0017-design-lenses.md](RES-0017-design-lenses.md) - the five lenses and
  what survived the strip from their donor project.
