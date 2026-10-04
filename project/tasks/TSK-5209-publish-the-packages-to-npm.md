---
id: TSK-5209
artifact: task
status: approved
revised: 2026-10-04
epic: EPC-2720
closes: [REQ-4140]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Publish the packages to npm and verify the install

The release workflow places all six platforms' binaries in each package's
`bin/` before packing, publishes each tarball to npm under `@meowshed`
with provenance, and the install is verified from a machine that holds no
meowpaw checkout.

## Acceptance criteria

1. Given each package directory, when `npm pack --dry-run` runs, then the
   tarball contents list `bin/<triple>/meow` for all six platforms. Closed
   by: the dry-run's contents output for all six packages.
2. Given a machine with no meowpaw checkout, when
   `pi install npm:@meowshed/meow-core` runs, then it succeeds and a Pi
   session quotes the reply shape. Closed by: the install and session test
   recorded in the task's Evidence.
3. Given an npm install, when the session loads, then the `postinstall`
   leaves no archive and makes no request. Closed by: the installer's
   `existsSync` early exit and the install's log.
4. Given the release workflow run with `NPM_TOKEN` set, when the publish
   step runs, then six packages publish with provenance. Closed by: the
   workflow run's publish step output.

## What to do

Each `package.json` gains `publishConfig.access: "public"`; the release
workflow's packing step copies the six platforms from the `bin-full-*`
artifacts into each package's `bin/` before `npm pack`, and a publish job
runs `npm publish --provenance --access public` for each package under a
token from the `NPM_TOKEN` secret. The install instructions in every
package's README and in the unit pages name the npm command first and the
local path as the development install.

## Depends on

- The `NPM_TOKEN` secret (blocking): a person holds the npm account with
  the `@meowshed` scope and sets the repository secret, because publishing
  is a public act a person answers for.

## Evidence

Not yet. This line stays first until every verb has passed.

## Left alone

The GitHub releases of the package archives, which stay as the record of
what shipped and the git install's download source; the local-path
installs, which stay as the development install; the Claude Code
marketplace, which this task doesn't touch.
