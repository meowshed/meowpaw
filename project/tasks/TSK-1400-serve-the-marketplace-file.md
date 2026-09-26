---
id: TSK-1400
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1090
closes: [REQ-1485]
issue: 176
---

# Serve the marketplace file at meow.retran.me

One task, one branch, one pull request, one review.

## What to do

The owner creates `retran/meow.retran.me` with Pages published by GitHub
Actions and `meow.retran.me` as its custom domain, adds a `CNAME` record for
`meow` pointing at `retran.github.io` at EuroDNS, and stores a fine-grained
token that can write to that repository alone as `MARKETPLACE_DISPATCH_TOKEN`
in `meowshed/meowpaw`.

Write the site's workflow: on a `repository_dispatch` of type
`meowpaw-release`, and by hand, download the `marketplace` release's
`marketplace.json` and deploy it at `meowpaw/marketplace.json`. Add a step to
`.github/workflows/release.yml` that sends the dispatch after publishing, and
fails the run, naming the step, when it can't.

Test the decision first: add the address on a clean machine, install a unit,
raise that unit's version in a release, and run `claude plugin marketplace
update meowpaw` and `claude plugin update`. If the update doesn't bring the new
version, stop and report, because ADR-1120 is then reversed.

## Depends on

Nothing. ADR-1120 is approved, and SPC-1080 states it.

## Evidence

Not yet. The task closes on the address adding a `url` marketplace on a clean
machine, a raised version installed by `marketplace update` and `plugin
update`, and a release run whose dispatch the site's deployment follows.

## Left alone

The install instructions, which TSK-1410 changes.
