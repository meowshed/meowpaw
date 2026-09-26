---
id: EPC-1090
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1120
checked-at:
---

# One marketplace address that serves every release

Realises exactly one authorising record, ADR-1120. The epic is complete when
`https://meow.retran.me/meowpaw/marketplace.json` serves the released
marketplace file, a release updates it with nothing done by hand, and every
install instruction gives that address.

## Acceptance criteria

Taken from ADR-1120, from its list of how I will know it was realised, before
the tasks below were written:

1. `claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json`
   adds a `url` marketplace named `meowpaw` on a clean machine, and a unit
   installs from it.
2. After a release that raises a unit's version, `claude plugin marketplace
update meowpaw` followed by `claude plugin update <unit>@meowpaw` installs
   the new version with nothing downloaded by hand.
3. The release workflow's run shows the dispatch sent, and the Pages
   deployment of `retran/meow.retran.me` that follows it serves the new file.
4. Every install instruction outside the record gives the one command.
5. Every requirement ADR-1120 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1400 the site and the dispatch: the owner's setup, the site's
      workflow in `retran/meow.retran.me`, the dispatch step in `release.yml`,
      and the test that `marketplace update` fetches a `url` marketplace again
      closes: REQ-1485
      evidence: the address added as a `url` marketplace on a clean machine,
      `meow-method` updated from 0.1.0 to 0.1.1 by `marketplace update` and
      `plugin update`, and the release's dispatch followed by the site's
      deployment, in #176.

- [x] T-002 TSK-1410 every install instruction gives the address, and this
      machine moves to it
      evidence: no install instruction outside the record downloads the file,
      and this machine's `meowpaw` has the address as its source, in #177.
      depends: TSK-1400 - the address has to serve the file before anybody is
      told to add it

## Coverage

ADR-1120 addresses one requirement, and T-001 closes it. `meow-method check
coverage` compares the decision's `addresses` against the union of the tasks'
`closes`.

T-001 tests the decision first: if `marketplace update` doesn't fetch a `url`
marketplace again, ADR-1120 is reversed, T-002 is dropped with that reason, and
the download form stays.

## Not covered

A domain of the organisation's own, and signing the marketplace file, as
ADR-1120 says.
