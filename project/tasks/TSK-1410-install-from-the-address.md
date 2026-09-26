---
id: TSK-1410
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1090
closes: []
issue: 177
---

# Give the address in every install instruction

One task, one branch, one pull request, one review.

## What to do

Change every install instruction outside the record, in `docs/` and the root
`README.md`, to `claude plugin marketplace add
https://meow.retran.me/meowpaw/marketplace.json`, and say how to turn on
auto-update. Remove the note in SPC-1080 that the download form is the one that
works, and keep the download form as a fallback. Move this machine's
`meowpaw` marketplace from the downloaded file to the address.

## Depends on

TSK-1400, because the address has to serve the file first.

## Evidence

Not yet. The task closes on `grep` finding no install instruction outside the
record that downloads the file, and `claude plugin marketplace list` showing
`meowpaw` with the address as its source on this machine.

## Left alone

The release archives and the `marketplace` release, which stay as they are.
