---
id: RES-0258
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0033, RES-0253
---

# The defect template

## Summary

A defect is the one artifact kind that authorises work without a decision
behind it, so its template is mostly about provenance. The published fields map
one to one onto the failures each prevents. Two additions belong to this
method. The requirement it violates, where one exists. And where none does,
saying so, because the defect is then evidence that the requirements have a
gap, and not only the code.

Research for the shape of a defect record: the one artifact kind that
authorises work without a decision behind it.

One of nine template documents, one per artifact kind in the record.

It does not cover how defects are tracked and planned, which is
[RES-0033-defects.md](RES-0033-defects.md).

## The question

The model authorises work with two kinds of record: a decision and a defect.
Everything else derives from them. A decision is argued; a defect is observed.

So this template's question is what an observation has to contain to authorise
work, and the answer is mostly about provenance.

## Method

The published templates were fetched and read on 2026-09-20 for the field
set and for the severity-against-priority distinction, and the testing
standard's naming of this document was read for the vocabulary problem it
records.

The standard's own text was not obtained beyond the publicly readable copy
consulted, which is enough for the naming point and not for anything more.

The sanitisation requirement is not from those sources; it comes from this
project's prohibition on handling secret material, applied to the one place a
credential most often appears.

## Findings

### The established fields, and what each one prevents

The practitioner consensus is consistent across the published templates, and
each field maps to a specific failure it prevents:

| Field                             | Prevents                                                                |
| --------------------------------- | ----------------------------------------------------------------------- |
| One defect per report             | A report that cannot be closed because half of it is fixed              |
| Expected against actual           | A report where the reader must guess what was wrong                     |
| Ordered reproduction steps        | A defect nobody else can see                                            |
| The exact environment and version | A fix for a problem that never existed here                             |
| Evidence                          | A description of a log rather than the log                              |
| Frequency                         | A race treated as a deterministic bug, or the reverse                   |
| Impact                            | Severity argued from vehemence                                          |
| Severity with its reason          | A severity nobody can dispute because nobody can see how it was reached |
| Triage decision                   | A report that sits between reported and accepted forever                |
| Retest tied to a version          | A defect closed against a build nobody shipped                          |

The standard for test documentation calls this class of document an incident
report, and notes the terms it goes by: anomaly, bug, defect, error, issue,
problem, trouble. That list is itself a finding. The vocabulary is unstable, so
a project declares which word it uses and uses one.

### Severity and priority are two fields and are routinely merged

The published distinction: **severity is how bad it is; priority is when it
gets fixed.**

Merging them produces the argument every team has had: a cosmetic defect on the
front page against a data-loss defect in an unused feature. One number has to
carry both, and it carries neither.

Keeping them separate also matches how this method divides things. Severity is
a property of the observation and belongs to the person who found it, and
priority is a scheduling decision that belongs with the work, where the record
holds none of it.

So: **the defect carries severity and its reason; it does not carry priority.**
Scheduling lives where scheduling lives.

### Evidence here has a constraint the published templates do not have

Every practitioner template asks for screenshots, logs and console output. This
project has a standing prohibition on reading, printing or transmitting a
repository's secret material. A defect report is one of the two places somebody
is most likely to break it, and a packed repository is the other.

A failing log is exactly where a connection string, a token or a key appears,
and the person pasting it is not looking for one.

So the template requires evidence and requires it **sanitised**, and it states
that as an obligation, where a reminder is forgotten, because the failure is an
omission nobody decided on.

### What this method adds that the published templates lack

The requirement it violates, where there is one. A defect is an observation
that something is wrong, and _wrong_ means against something. Where a
requirement exists, citing it turns the defect from a complaint into a
falsifiable claim and gives verification something to close against.

Where no requirement exists, that is the more interesting case and the template
must not hide it: the defect is evidence that a requirement is missing, and the
honest record says so, inventing nothing retrospectively. A defect that reveals
a gap in the requirements is a finding about the record as well as about the
code.

The revision it was observed at. The corpus dates evidence by tree
revision, and a defect is evidence. Without it, a report cannot be
distinguished from one about code that has since changed.

What was tried. A defect found after three hypotheses were eliminated is a
more valuable record than one found immediately, and the eliminated hypotheses
are what stop the next person repeating them. This is the same field the
development log requires, and for the same reason.

### The triage decision is part of the record

A report that nobody has decided about is the commonest dead state in any
tracker. The template makes the decision a field: accepted, not a defect, a
duplicate of a named record, or deferred with the reason.

_Not a defect_ deserves a place because it is a real outcome and is usually
recorded nowhere, which means the same observation is reported again in six
months.

### The sections it carries

| Section             | Holds                                                                                                        | Mandatory        |
| ------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------- |
| Front matter        | Identifier, kind, status, revision date, the requirement violated where one exists, the revision observed at | Yes              |
| Title               | The wrong behaviour, in one line                                                                             | Yes              |
| Expected and actual | What should happen and what does                                                                             | Yes              |
| Reproduction        | Ordered steps, from a stated starting state                                                                  | Yes              |
| Environment         | Versions, platform, configuration that matters                                                               | Yes              |
| Frequency           | Always, sometimes with a rate, or once                                                                       | Yes              |
| Evidence            | Sanitised output, logs or files                                                                              | Yes              |
| Impact and severity | What it costs, and the severity that follows                                                                 | Yes              |
| Triage              | Accepted, not a defect, duplicate, or deferred with a reason                                                 | Yes              |
| What was tried      | Hypotheses eliminated, where any were                                                                        | Where applicable |

### What the template must refuse

Two defects in one record.

A report with no reproduction and no explanation of why it cannot be
reproduced. _Happens sometimes_ is a frequency, and it substitutes for no
steps.

Unsanitised evidence.

A severity with no reason.

A fix in the report. A defect is an observation; the fix is a task, so somebody
reviews it as a change, where a description is only agreed to.

## Conclusions

1. One defect per record, so it can be closed. 2. Expected and actual are both
   stated, since a report giving only one leaves the reader to guess. 3.
   Reproduction is ordered and starts from a stated state, or the report says
   why it cannot be reproduced and gives the frequency instead. 4. The
   environment and versions are exact. 5. Evidence is required and is
   sanitised, because a failing log is where a credential appears and the
   prohibition on handling secret material has to survive the one place it is
   most likely to be broken. 6. The revision it was observed at is recorded,
   because a defect is evidence and evidence names its revision. 7. The
   violated requirement is cited where one exists, which turns the report into
   a falsifiable claim with something to close against. 8. Where no requirement
   exists, the record says so, since the defect is then evidence that the
   requirements have a gap. 9. Severity carries its reason and priority is not
   recorded here, severity being a property of the observation and priority a
   scheduling decision. 10. The triage decision is a field, including _not a
   defect_, so the same observation is not reported again. 11. Eliminated
   hypotheses are recorded where any were, so the next reader does not repeat
   them. 12. The fix is a task and no part of the report, so somebody reviews
   it as a change.

## Sources

All read 2026-09-20.

- [Bug report template for reproduction, triage and retest](https://playcode.io/blog/bug-report-template)
  - one observed defect with expected and actual behaviour, ordered
    reproduction steps, the exact environment and version, sanitised evidence,
    measured frequency and impact, a severity rationale, a human triage decision,
    and a retest tied to the target fix version.
- [How to create a bug report template](https://birdeatsbug.com/blog/how-to-create-bug-report-template)
  and [Bug report template 2026](https://crosscheck.cloud/blogs/perfect-bug-report-template-free/)
  - the environment fields that matter, and the distinction that severity is
    how bad the defect is while priority is when it should be fixed.
- [ISO/IEC/IEEE 29119-3 test documentation](https://wildart.github.io/MISG5020/standards/ISO-IEC-IEEE-29119-3.pdf)
  - the incident report as the standard's name for this document, and the list
    of terms it is otherwise known by, which is why a project declares one word
    and uses it.
- [RES-0033-defects.md](RES-0033-defects.md) - the defect as one of two records
  that authorise work, and the gap in the model it fills.
- [RES-0018-dev-log.md](RES-0018-dev-log.md) - the refuted-hypothesis field and
  why it is the part most useful to the next reader.
