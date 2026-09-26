---
id: ADR-1120
artifact: adr
status: draft
revised: 2026-09-26
addresses: [REQ-1485]
supersedes: []
---

# 1120. The marketplace is served from meow.retran.me

## Decision

The released `marketplace.json` is served at
`https://meow.retran.me/meowpaw/marketplace.json`, and a person adds it once:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
```

The address is the GitHub Pages site of a repository `retran/meow.retran.me`,
which the owner's personal account owns, with `meow.retran.me` as its custom
domain and a `CNAME` record for `meow` pointing at `retran.github.io` at
EuroDNS. The path leaves the rest of `meow.retran.me` for whatever else the
organisation publishes later. The repository holds one workflow. It downloads
the `marketplace.json` asset of `meowshed/meowpaw`'s `marketplace` release and
deploys it to Pages at `meowpaw/marketplace.json`. It runs when
`meowshed/meowpaw`'s release workflow sends it a `repository_dispatch` after
publishing, and when someone starts it by hand.

The release workflow sends the dispatch with a fine-grained token that can
write to `retran/meow.retran.me` alone, stored as a secret in
`meowshed/meowpaw`. Where the dispatch fails, the release stays published, and
the step fails so the run says the address is behind. The `marketplace`
release keeps its asset, so the download-and-add form RES-0274 recorded keeps
working beside the address.

## Why

REQ-1485 asks for one address serving every release, and RES-0275 found that
an address outside `github.com` is a `url` marketplace, which the platform's
update refreshes. The owner offered `meow.retran.me`, and a domain the
owner controls outlives the forge: moving off GitHub later changes where the
file is served from and leaves the address people added unchanged.

`retran.me` is verified for the owner's personal account, and RES-0275 found
that this lets only that account's repositories publish to the domain and its
immediate subdomains. A repository under `retran` serves the subdomain, and
`meowshed/meowpaw` couldn't.

## Alternatives

| Option                                                             | Better at                                        | Why it lost                                                                                         |
| ------------------------------------------------------------------ | ------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| `retran/meow.retran.me` served at `meow.retran.me`                 | A host of its own the owner controls             | Chosen                                                                                              |
| A project site `retran/meowpaw`, served at `retran.me/meowpaw`     | No DNS change                                    | The address sits inside the owner's homepage, and anything else the organisation publishes joins it |
| The homepage `retran/retran.github.io` fetches the file            | No new repository                                | Every release rebuilds the homepage, and a failed fetch can break the owner's own site              |
| `meowshed/meowpaw` serving a subdomain of `retran.me`              | No token for another repository                  | `retran.me`'s verification lets only the owner's personal repositories publish to its subdomains    |
| Drop `retran.me`'s verification so `meowshed/meowpaw` can serve it | One repository, no token, the release deploys it | `retran.me` and every subdomain lose their protection from takeover, the owner's homepage included  |
| `meowshed.github.io/meowpaw` deployed by the release workflow      | No token and no domain; one workflow does it all | The address names the forge, so leaving GitHub changes the address everybody added                  |
| Keep downloading the file and adding it by its path                | Costing nothing                                  | REQ-1485: a person learns of a release only by fetching the file again                              |

## What it costs

A second repository, `retran/meow.retran.me`, with one workflow and Pages
turned on, one `CNAME` record at EuroDNS, and a fine-grained token that the
owner creates, renews when it expires, and stores as a secret. A release waits for a Pages deployment before its address
serves it, which takes about a minute.

A person turns on auto-update for the marketplace once, under `/plugin`, or
runs `claude plugin marketplace update meowpaw` for each release, because
auto-update is off by default for every marketplace that isn't Anthropic's.

## What would reverse it

- The test the epic runs first shows `claude plugin marketplace update` doesn't
  fetch a `url` marketplace again, so no address serves REQ-1485 and the
  download-and-add form stays.
- The owner stops controlling `retran.me`, and the address moves to a domain
  of the organisation's own.
- The platform starts treating addresses on `retran.me` as git forms, or
  follows a `github.com` release address as a file.

## Consequences

- `retran/meow.retran.me` is created with Pages published by its workflow and
  `meow.retran.me` as its custom domain, and the `CNAME` record exists.
- `meowshed/meowpaw`'s release workflow dispatches to it after publishing.
- SPC-1080's release section, `docs/README.md`, each unit's page and the root
  `README.md` give the one `marketplace add` command with the address.
- People who added the file by its path move to the address once, by removing
  the marketplace and adding it again.

## How I will know it was realised

1. `claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json`
   adds a `url` marketplace named `meowpaw` on a clean machine, and a unit
   installs from it.
2. After a release that raises a unit's version, `claude plugin marketplace
update meowpaw` followed by `claude plugin update <unit>@meowpaw` installs
   the new version with nothing downloaded by hand.
3. The release workflow's run shows the dispatch sent, and the Pages
   deployment of `retran/meow.retran.me` that follows it serves the new file.
4. Every install instruction outside the record gives the one command.

## What this does not settle

- A domain of the organisation's own, which a later decision can move to by
  serving the same file there.
- Signing the marketplace file.
