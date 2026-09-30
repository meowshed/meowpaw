---
id: ADR-2320
artifact: adr
status: approved
revised: 2026-09-30
addresses: [REQ-3322]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2320. The read-back listing starts at the earliest created issue's own `updated_at`

## Decision

`project` starts its read-back listing,
`repos/{r}/issues?state=all&since=<start>&per_page=100`, at the earliest
`updated_at` among the issues the run created, as each create's answer
states it (REQ-3322). Where no create's answer carries a readable
`updated_at`, `<start>` is the `Date` of the run's first response, as
ADR-1810 set it. This replaces ADR-1810's sentence that `<start>` is the
`Date` of the run's first response, and nothing else in ADR-1810 changes.

Once this is accepted, a run given the repository's name whose first task is
unmapped reads back every issue it created, whichever second GitHub stamped
the first create's answer with. What still doesn't work: an issue whose
create answer carries no `updated_at` falls back to the old start, and so
keeps the old failure for that run.

## Why

GitHub's `since` includes an issue updated in the second it names and leaves
out one updated a second earlier (RES-0312). The first response's `Date` is
the moment GitHub answered, which can be a second after it wrote the issue,
and when the repository is named the first response is the first create's
(RES-0312). The issue's own `updated_at` is GitHub's time for the very thing
the listing has to find, and a create's answer carries it as a required field
(RES-0312), so no margin has to be guessed.

## Alternatives

| Option                                           | Better at                                                                            | Why it lost                                                                                                                           |
| ------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                       | No change, and the failure is safe: the next run reads the issue through its mapping | A run that did all its work reports a partial result and exits 3, which a person or a loop then acts on                               |
| The first `Date` less 60 seconds                 | One line, and covers any offset under a minute                                       | The margin is a guess, and a wider window lists more pages in a busy repository                                                       |
| A read of the repository before the first create | Keeps ADR-1810's sentence true as written                                            | Costs a request the run doesn't otherwise need, and a read in the same second as the create still relies on the second being included |
| The earliest created `updated_at` (chosen)       | GitHub's own time for the issues the listing must find                               | Needs the field in each create's answer, so it keeps a fallback                                                                       |

## What it costs

`project` keeps the earliest `updated_at` it has seen across the run, and the
check for criterion 1 needs a stand-in whose issue is written a second before
its answer is sent. A reader of ADR-1810 has to read this decision to know
where the listing starts.

## What would reverse it

- A create's answer on GitHub observed with an `updated_at` later than the
  same issue's `updated_at` in the listing that follows, with nothing between
  them updating the issue.
- GitHub documenting `since` as exclusive of the second it names, or a
  listing observed leaving out an issue whose `updated_at` equals `since`.

## Consequences

- SPC-1080's section "Projecting the record onto a tracker" states the new
  start and its fallback.
- ADR-1810's Decision gains a line naming this decision as its amendment.
- TSK-4020 realises this decision with no epic.

## How I will know it was realised

1. A check runs `project` against a stand-in that writes each issue a second
   before the `Date` of the answer it sends, with the repository named and
   the first task unmapped. The listing's `since` equals the first issue's
   `updated_at`, every created issue reads back, and the run exits 0.
2. A check whose create answers carry no `updated_at` shows the listing
   starting at the first response's `Date`.

## What this does not settle

- Whether `project` reads created issues back in one listing at all, which
  ADR-1810 settled.
- Any other request's start or window, such as `history`'s listings.
