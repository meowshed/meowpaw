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

Every install instruction outside the record, in the seven unit pages,
`docs/README.md` and the root `README.md`, adds the marketplace by its
address, and the two indexes say how to turn on auto-update. SPC-1080 keeps
the download form as a fallback.

```text
$ grep -rn 'curl -fsSLo marketplace.json' --include='*.md' --exclude-dir=project . | wc -l
0
$ grep -rln 'meow.retran.me/meowpaw/marketplace.json' --include='*.md' --exclude-dir=project . | wc -l
9
$ claude plugin marketplace list
  ❯ meowpaw
    Source: URL (https://meow.retran.me/meowpaw/marketplace.json)
```

This machine's six units, reinstalled from the address, each printed
"Successfully installed".

## Left alone

The release archives and the `marketplace` release, which stay as they are.
