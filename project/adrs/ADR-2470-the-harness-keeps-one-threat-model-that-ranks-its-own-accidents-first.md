---
id: ADR-2470
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2784, REQ-2786, REQ-2788, REQ-2790, REQ-2792]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2470. The harness keeps one threat model, which ranks its own accidents first

## Decision

The harness's threat model is a section of the specification that states
the quality attributes, written once and rewritten as the harness changes,
because a specification is living and a threat model describes the present.
It works through STRIDE, the published taxonomy of six categories that
OWASP's threat-modelling process uses, and maps each category to the control
that answers it, or says none does (REQ-2786).

It considers accidents by a legitimate insider before attackers (REQ-2784),
and the first insider it names is the harness itself, acting on a repository
it has just met (REQ-2792). It marks each place where data changes trust
level: a repository's files read into a prompt, a tracker's issue text, a
pull request comment and a tool's output (REQ-2788). It ranks each threat as
likely or unlikely and as severe or minor, in words and with no numeric score
(REQ-2790).

Once this is accepted, a decision that adds a trust boundary has a document to
update and a list to rank against. What still doesn't work: the model is
prose, so no check reads it, and review holds it.

## Why

RES-0214 read a `threat-model` skill and found that a model built from
external attacks first misses the likeliest damage, which in an agent
harness is the agent running a destructive command on a repository it
misread. It found that the donor standard gives no enumeration, so a
published taxonomy is the checklist that keeps a model from listing only the
threats its author thought of, and that a numeric score is false precision.
It also warns that a taxonomy used as a template produces an enterprise
document for a project with one user, so the model uses STRIDE as a checklist
and stays short.

## Alternatives

| Option                      | Better at                         | Why it lost                                                     |
| --------------------------- | --------------------------------- | --------------------------------------------------------------- |
| Do nothing                  | No document to keep               | Five requirements stay open and no decision has a model to cite |
| A threat model per decision | Each record carries its own risks | Risks across decisions never meet in one ranking                |
| A numeric score per threat  | A sortable list                   | RES-0214 found the scores are guesses written as numbers        |

## What it costs

The specification gains a section that must change whenever a decision adds a
trust boundary, and the design step has one more document to check.

## What would reverse it

- A later research record finds a taxonomy for agent harnesses whose
  categories STRIDE doesn't cover.

## Consequences

The spec step writes the section. The design step's instructions point at it
for a decision with a security-relevant boundary, as design rule D20 asks.

## How I will know it was realised

1. The specification carries the section, and its categories are STRIDE's six,
   each mapped to a control or marked uncovered (REQ-2786).
2. Its first ranked threat is an accident by the harness (REQ-2792).
3. It lists each trust boundary and ranks threats in words (REQ-2788,
   REQ-2790).

## What this does not settle

- Which controls the harness adds for a threat the model finds uncovered.
  Each is its own decision.
