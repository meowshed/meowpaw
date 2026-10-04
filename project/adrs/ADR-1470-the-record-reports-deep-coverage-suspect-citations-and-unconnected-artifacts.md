---
id: ADR-1470
artifact: adr
status: done
revised: 2026-09-27
addresses: [REQ-0139, REQ-0141, REQ-0143, REQ-0161]
supersedes: []
---

# 1470. The record reports deep coverage, suspect citations and unconnected artifacts

## Decision

`paw` checks each citation against the whole chain above it and against the
date its target was revised. `paw check` fails where the author of the change
can clear the finding, and `paw status` reports what only a new record can fix:
unconnected artifacts, suspect citations in approved records, approved records
over a rejected provider and how much of the requirement set rests on
judgement.

`check coverage` walks each approved or living artifact up its relations to
the research it rests on. It reports each provider on the way that is still a
draft, naming the chain, such as `TSK-NNNN -> REQ-NNNN -> RES-NNNN (draft)`,
because approving or rejecting that draft clears it (REQ-0139). Where the
artifact is itself a draft or living, it also reports a provider that is
withdrawn or superseded, because that artifact can still be moved off it. An
approved artifact over a rejected provider goes to `status`, because only a new
record can clear it. I define a provider as covered when it was accepted,
because the project record's chain runs from research to task, and an item
resting on an unaccepted input is the defect the method's order exists to stop.

A citation is suspect when its target's `revised` date is later than the
citing record's own (REQ-0141). An epic or a defect as a target is compared by
status and not by date, because both kinds change after approval by design: an
epic as its tasks close, and a defect as its Tasks and Closed by sections fill.
A citation of an epic or a defect that is withdrawn or superseded is still
suspect. `check relations` reports a suspect citation in a draft or a living
artifact, which revising that artifact clears. In an approved artifact, which
can't be revised to clear it, `show` marks the citation in its `Names` list and
`status` counts it.

`status` lists each approved or living artifact that cites nothing and that
nothing cites, and `check` doesn't fail on one (REQ-0143). A draft is left out
because it is still being written, and what cites it usually arrives in a
later change: requirements elaborate research only after the research is
approved. A withdrawn, rejected or superseded record is left out because it is
kept as the record that somebody considered the question, and nothing is meant
to build on it.

`status` counts the requirements in force by their `verification` field,
static, behavioural, evaluation and judgement, with judgement split by its
`verifier`. It states the share resting on evaluation or judgement (REQ-0161).

A one-off script over the front matter measured the record before I wrote
this decision, and realisation item 4 counts again with `paw status`:

- No approved or living artifact rests on a draft or rejected provider.
- Three approved records carry a suspect citation: ADR-1020 addresses REQ-1140,
  and ADR-1350 and TSK-2020 cite REQ-3166. REQ-1140 and REQ-3166 were both
  withdrawn after these citations.
- Five approved artifacts are unconnected. TSK-1000, TSK-1100 and TSK-1220 are
  planning tasks approved before ADR-1440, which name no authority. BUG-1130
  and BUG-1150 were closed by a change before a defect authorised tasks, and
  name no requirement, as the defect template allows where none covers the
  defect.
- 61 of the 1,091 requirements in force rest on evaluation or judgement.

After this decision a record resting on a draft fails the check, as does a
draft or a living artifact citing an artifact revised after it. `show` and
`status` report the cases only a new record can fix, and the `run` skill shows
`status` first whenever the method runs.

What still doesn't work:

- `revised` is a date, so a target revised on the same day as the citation
  isn't suspect. That includes a requirement withdrawn on the day an approved
  record cites it, which no check then reports.
- A draft or living artifact revised for any reason clears its suspect
  citations, whether or not the edit addressed them.
- A task, an epic or a defect gets a later `revised` date when it changes after
  approval. A target revised between the citation and that change then no
  longer counts as later, so its suspect citation is missed.

## Why

RES-0067 found that the tools which check a traced corpus report two defects
this record doesn't check. One is a transitive defect: an item's own links
resolve while a provider above it is undercovered. The other is a suspect link,
whose target changed after the link was written. RES-0067 also found that a
false positive in a corpus check is a defect, because such a check runs on
every change and one that fires wrongly is switched off.

That second finding sets where each report goes. `check` fails only where the
author of the change can act: a draft or a living artifact can be revised, and
a draft provider can be approved or rejected. An approved record can't be
revised. A permanent failure on one would teach every contributor to ignore the
check, so the frozen cases go to `status`, which reports and fails nothing.

RES-0070 found that judgement is weaker evidence than a mechanical check and
that the corpus should report how much of itself rests on judgement. Every
requirement already declares its `verification`, so the count costs one pass
over the requirements.

The strongest objection: a report in `status` that nothing fails on is one
nobody reads. The `run` skill's first step shows `status` whenever the method
runs, and each item it lists is one the amendment path resolves with a new
record, which a failing check can't ask for.

## Alternatives

| Option                                                          | Better at                                       | Why it lost                                                                                                                                        |
| --------------------------------------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                      | No change                                       | REQ-0139, REQ-0141 and REQ-0143 stay unmet, as ADR-1100 left them                                                                                  |
| Fail `check` on every suspect citation and unconnected artifact | One place to look                               | Eight findings on approved records nobody can edit, so the check is switched off, as RES-0067 warns                                                |
| Compare the commits that last changed each file                 | Catches a revision on the same day              | Needs the full history, which a shallow clone lacks, and a squash merge moves every file in a change to one commit, which says nothing about order |
| Store a fingerprint of the target in each citation              | Exact: any change to the target's text is found | A citation becomes more than a bare identifier, against REQ-0644, and every approved record would need one added                                   |
| Count only `judgement` as resting on judgement                  | A smaller share                                 | An evaluation is scored by a model, which is a judgement with a loop around it, so leaving it out understates the share                            |

## What it costs

`check coverage` walks every chain on each run, one pass over the relations per
artifact. `status` grows four parts, and `show` marks suspect citations. The
kinds compared by status are a list in `meow-flow`, and whoever adds a kind
that changes after approval has to add it there, or its citations turn suspect
each time it changes.

## What would reverse it

I would move to commits or fingerprints if the same-day blind spot let a real
suspect citation through, shown by a defect. I would fail `check` on the frozen
cases if the amendment path gained a way to clear them without editing the
frozen record.

## Consequences

- `paw check coverage` reports an approved or living artifact over a draft
  provider, and a draft or living one over a withdrawn or superseded provider.
- `paw check relations` reports a suspect citation in a draft or living
  artifact.
- `paw show` marks a suspect citation.
- `paw status` lists unconnected artifacts and approved records over a
  rejected provider, counts suspect citations in approved records and states
  the share resting on judgement.
- SPC-1100 states these four commands' new reports.

## How I will know it was realised

1. Fixtures show `check coverage` failing on an approved artifact over a draft
   provider two steps up and passing once the provider is approved, failing on
   a draft over a withdrawn provider, and `status` listing an approved artifact
   over a rejected one.
2. Fixtures show `check relations` failing on a draft citing a target revised
   later, and passing on an approved record doing the same, which `show` marks
   and `status` counts.
3. A fixture shows a citation of an epic revised later passing, and one of a
   withdrawn epic reported as suspect.
4. `status` on the project record lists the five unconnected artifacts, the
   three suspect citations and the share resting on judgement with judgement
   split by verifier, matching the counts above.
5. `paw check` passes on the project record after the change.
6. Every requirement ADR-1470 addresses lands in exactly one closed task.

## What this does not settle

- Clearing a suspect citation in an approved record without a new record.
- Whether an unconnected approved artifact should be withdrawn, which is the
  owner's call for each one.
