---
id: TSK-1380
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1080
closes: [REQ-0074, REQ-3178]
issue:
---

# Release the units with their binaries

One task, one branch, one pull request, one review.

## What to do

Confirm first that a marketplace can be added from a released file's address,
and change SPC-1080 if it can't. Then write `.github/workflows/release.yml`:
build all six targets for each unit that changed, pack each unit with its
binaries as an archive, and publish the archives with their SHA-256, their
sizes and a marketplace file pointing at them by `url` and `sha256`. Each
unit's archive carries its own version (REQ-0074), and a person installs it
with nothing else (REQ-3178).

## Depends on

TSK-1350, TSK-1360 and TSK-1370, because a release carries every ported unit.

## Evidence

Release run 36232216779 built all six targets and published a release for
each unit, tagged `<unit>-v<version>`, and a `marketplace` release whose notes
list every archive's size and SHA-256:

```text
$ gh run watch 36232216779 --exit-status
exit=0
$ gh release list
Marketplace       Latest  marketplace
meow-git 0.1.0            meow-git-v0.1.0
meow-scm 0.2.0            meow-scm-v0.2.0
meow-verbs 0.2.0          meow-verbs-v0.2.0
meow-prose-gate 0.1.1     meow-prose-gate-v0.1.1
meow-prose 0.3.4          meow-prose-v0.3.4
meow-core 0.6.0           meow-core-v0.6.0
```

The archives are 1,675,980 bytes for meow-verbs, 3,928,000 for meow-scm and
1,768,656 for meow-git. In a `debian:bookworm-slim` container on ARM64, with
`python3: absent  node: absent`, Claude Code 2.1.283 installed `meow-verbs`
and `meow-git` from the released marketplace, `stat` showed `-rwxr-xr-x` on
both launchers and their binaries, and both units ran:

```text
$ meow-verbs run test
summary: test passed
exit=0
$ echo '{"tool_input":{"command":"git push"}}' | meow-git push-guard
meow-git push-guard: no commit to publish was found; checked nothing
exit=0
```

Adding the marketplace by its release address failed, because Claude Code
reads an address on `github.com` as a git repository. Adding the downloaded
file by its path worked, so SPC-1080, the workflow's notes and
`docs/README.md` now give that form, and RES-0274 records the finding. This
closes REQ-0074, since each unit is released under its own version, and
REQ-3178, since a person installs a unit with nothing else.

## Left alone

Signing the binaries.
