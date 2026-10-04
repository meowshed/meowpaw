---
id: ADR-2340
artifact: adr
status: done
revised: 2026-09-30
addresses: [REQ-3322]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2340. An issue the read-back listing leaves out is read by its number before it is reported

## Decision

After the read-back listing, `project` reads by its number each issue it
created that the listing left out, `repos/{r}/issues/{n}`, uncached, through
the request layer (REQ-3322). An issue that reads back as written is
projected. One that reads differently, or can't be read, goes under
`created, not read back` with that reason. A throttle, a ceiling or a 401
during these reads stops them as it stops any other request, and each issue
left unread goes under `created, not read back` with the reason
`no read ran`. Where the listing itself failed or didn't run, no read by
number is sent, as today.

This amends ADR-1810's read-back, which read created issues in one listing
alone, and leaves ADR-2320's start of the listing as it is.

Once this is accepted, a run whose listing lags its creates reads every
created issue back and exits 0, at the cost of one request per issue the
listing missed. What still doesn't work: an issue the listing missed and whose
read by number also misses it is reported as not read back, and nothing has
shown whether that can happen.

## Why

A listing sent straight after a create left out the issue just created in
both runs observed, and listed it about ten seconds later (RES-0313). A read
by number straight after each create found all six issues of the one run that
did so (RES-0313). Reading only the issues the listing missed keeps the
listing's saving where it works and pays a request only where it doesn't.

## Alternatives

| Option                                                 | Better at                                          | Why it lost                                                                                                       |
| ------------------------------------------------------ | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Do nothing                                             | One request per hundred issues, and a safe failure | Both observed runs reported a partial result and exited 3 though every create succeeded                           |
| Send the listing again after a wait                    | Keeps one listing                                  | The lag is neither documented nor measured, so the wait is a guess, and the run holds the terminal while it waits |
| Read every created issue by number and send no listing | One path, observed to work                         | Gives up the listing's saving where the listing does work                                                         |
| Read by number what the listing missed (chosen)        | Pays only for the issues the listing missed        | In the lagging case it costs a request per created issue                                                          |

## What it costs

In the lagging case a run sends one more request per created issue, as the
pack did before TSK-2960, and the budgets count each one. The read-back has
two paths, and the stand-in needs a way to leave an issue out of the listing
while still answering a read of it by number, which `omit` already does.

## What would reverse it

- A read by number observed missing an issue created in the same run, which
  would make the listing's lag no longer the only failure.
- GitHub documenting the listing as consistent with a create, or a
  measurement showing the lag below a second in every run of a month.

## Consequences

- SPC-1080's section "Projecting the record onto a tracker" states the reads
  by number.
- ADR-1810's Decision gains a line naming this decision as its amendment.
- `Partial.test_an_issue_the_listing_omits_is_not_read_back` changes, because
  an issue the listing omits and that reads back by number is projected.
- TSK-4040 realises this decision with no epic.

## How I will know it was realised

1. A check whose stand-in leaves one of two created issues out of the listing
   and answers a read of it by number shows both issues read back, one read
   by number sent, no `partial:` line, and exit 0.
2. A check whose stand-in leaves an issue out of the listing and answers its
   read by number with a different body shows the issue under
   `created, not read back` with `reads differently from what was written`.
3. A run with no issue left out of the listing sends no read by number.

## What this does not settle

- How long GitHub's listing lags a create.
- Whether `history` reads anything by number, which it doesn't.
