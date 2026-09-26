---
id: RES-0274
artifact: research
status: draft
revised: 2026-09-26
elaborates: RES-0273
---

# Installing from a released marketplace

## Summary

A marketplace file published as a GitHub release asset can't be added by its
address, because Claude Code reads any `https://` address on `github.com` as a
git repository and tries to clone it. Downloading the file and adding it by
its path works: the units install from their archives, each archive's SHA-256
is checked, the executable bits survive, and the units run on a machine with
neither Python nor Node.js. A marketplace added from a local file doesn't
follow later releases, so a person downloads the file again to get them.

## The question

RES-0273 found that a marketplace can pin a plugin to an archive by its
SHA-256, and SPC-1080 told a person to add the released `marketplace.json` by
its address. Does that command work for a file published on a GitHub release,
and does an installed unit keep the executable bits its launcher and hooks
need?

## Method

The first release ran from the workflow on 2026-09-26 and published six unit
archives and a `marketplace` release. I ran Claude Code 2.1.283, installed
with its own install script, in a `debian:bookworm-slim` container on ARM64
where `command -v` finds neither `python3` nor `node`. I tried three ways to
add the marketplace, installed `meow-verbs` and `meow-git`, read the installed
files' modes with `stat`, and ran both units. I read the marketplace reference
for the rule that decides a source's type.

## Findings

### A github.com address becomes a git source

`claude plugin marketplace add` with the release asset's address failed:

```text
✘ Failed to add marketplace: Failed to clone marketplace repository: ...
fatal: repository 'https://github.com/meowshed/meowpaw/releases/download/marketplace/marketplace.json.git/' not found
```

The marketplace reference states the rule: a `url` source is "An `http://` or
`https://` URL that doesn't match a git form", and a git form includes "an
`https://` URL that ... names a github.com or gitlab.com repository". An
address on `github.com` matches it whatever its path.

### A settings entry wasn't registered from the shell

A `url` source declared in `extraKnownMarketplaces` in `~/.claude/settings.json`
wasn't registered: `claude plugin marketplace list` printed "No marketplaces
configured", and `claude plugin marketplace update meowpaw` answered
"Marketplace 'meowpaw' not found". I didn't test it in an interactive session,
where the reference says such a declaration is loaded.

### A downloaded file installs from the archives

With the file downloaded by `curl` and added by its path, both installs
succeeded:

```text
✔ Successfully added marketplace: meowpaw (declared in user settings)
✔ Successfully installed plugin: meow-verbs@meowpaw (scope: user)
✔ Successfully installed plugin: meow-git@meowpaw (scope: user)
```

The reference says a `url` or `file` marketplace can't use relative-path
plugin sources, which the released file doesn't: each entry is an `archive`
source with an absolute `url` and a `sha256`.

### The executable bits survive the archive

`stat` shows `-rwxr-xr-x` on both launchers and on the Linux binaries for both
processors in the plugin cache, so the hooks that call `bin/meow-git` directly
run it.

### The units run without an interpreter

In a repository whose profile declares only `test = "echo ok"`,
`meow-verbs status` exited 0 and reported `test` resolved and the other four
verbs unresolved, `meow-verbs run test` exited 0 with "summary: test passed",
and `meow-git push-guard` exited 0 with "no commit to publish was found;
checked nothing".

## Conclusions

1. A person adds the released marketplace by downloading `marketplace.json`
   and adding it by its path, because its release address is read as a git
   repository.
2. A later release reaches that person only when they download the file again,
   so a marketplace address that follows releases needs a host outside
   `github.com`.
3. The archive install keeps the executable bits, so the launcher's fallback
   that sets them is a guard and not the path every install takes.
4. A released unit runs on a machine with neither Python nor Node.js.

## Sources

- [Plugin marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md),
  read 2026-09-26 - the input each marketplace source type is built from, and
  the `url` source's rule against relative-path plugins.
- Release run 36232216779 of `.github/workflows/release.yml`, 2026-09-26 - six
  unit releases and the `marketplace` release.
- Claude Code 2.1.283 in `debian:bookworm-slim` on ARM64, 2026-09-26 - the
  three ways to add the marketplace, the installed modes, and the units' runs.
