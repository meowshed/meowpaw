---
id: RES-0275
artifact: research
status: draft
revised: 2026-09-26
elaborates: RES-0274
---

# Where the marketplace file lives

## Summary

A marketplace file served from an `https://` address outside `github.com` and
`gitlab.com` becomes a `url` marketplace, which `claude plugin marketplace
update` fetches again, so a person gets a later release without downloading
anything by hand. `retran.me` is the owner's domain, served by GitHub Pages
from `retran/retran.github.io` and verified for the owner's personal account.
That verification lets only that account's repositories publish to the domain
and its immediate subdomains, so a repository under `retran` can serve
`meow.retran.me` with one CNAME record, while `meowshed/meowpaw` can't.
`meowshed.github.io/meowpaw/` needs no domain at all. None of these addresses
has been tried yet.

## The question

RES-0274 found that a released `marketplace.json` added by its path doesn't
follow later releases, and that an address following them needs a host outside
`github.com`. The owner offered `retran.me` and pointed at the homepage that
publishes it. Where can the file live so that one address serves every release,
and what does each place cost?

## Method

I read the marketplace reference and the pages on discovering plugins and on
loading them on 2026-09-26, and GitHub's pages on custom domains for Pages
from the `github/docs` repository the same day. I read the Pages settings of
`retran/retran.github.io` and `meowshed/meowpaw` through the GitHub API, the
homepage's deploy workflow, and the DNS records of `retran.me`. Nothing was
published, so no address below has been added to Claude Code.

## Findings

### Which addresses are url marketplaces

The marketplace reference builds a `url` source from "An `http://` or `https://`
URL that doesn't match a git form", and a git form is "an `https://` URL that
ends in `.git`, contains `/_git/`, or names a github.com or gitlab.com
repository". A `github.io` address or an owner's own domain matches no git
form. For a `url` source, "Claude Code downloads only that file", which the
released file allows, because every entry in it points at an archive by an
absolute `url`.

### Updating a url marketplace

`claude plugin marketplace update <name>` updates a marketplace's listing, and
`claude plugin update <plugin>@<marketplace>` updates one plugin. Auto-update
is off by default for every marketplace that isn't Anthropic's, and a person
turns it on under `/plugin` in the **Marketplaces** tab; after that, Claude Code
refreshes the marketplace after a session starts and updates the plugins
installed from it. The documentation doesn't say whether a `url` marketplace
is fetched again on update or only when added, which a test has to settle.

### retran.me

`gh api repos/retran/retran.github.io/pages` reports a site built by a
workflow, `cname` `retran.me`, `protected_domain_state` `verified`, HTTPS
enforced, and a certificate for `retran.me` and `www.retran.me`. The site is
built with Astro by `withastro/action` and deployed by `actions/deploy-pages` on
every push to `master`. `retran.me` resolves to GitHub Pages' four addresses,
`www.retran.me` is a CNAME for `retran.github.io`, and EuroDNS serves the
zone. `meow.retran.me` resolves to nothing, so it is free to use.

GitHub's documentation says a custom domain set on a user site "will be used
for all project sites owned by the same account", so a project site of a
repository `retran/<name>` appears at `retran.me/<name>`.
`https://retran.me/ide-development-2023/`, a project site of the owner's,
answers 200. The same page says verifying a domain for a personal account lets
"only repositories owned by your personal account" publish "to the verified
custom domain or the domain's immediate subdomains". A custom subdomain is set
in the repository's Pages settings and pointed at Pages by a `CNAME` record at
the DNS provider, and a site deployed by a workflow needs no `CNAME` file.

### meowshed

`meowshed/meowpaw` has no Pages site: the API answers 404. The organisation
declares no site of its own, and `https://meowshed.github.io/` answers 404. A
Pages site for `meowshed/meowpaw` would be served at
`meowshed.github.io/meowpaw/`, and a workflow can deploy it with the same
`actions/deploy-pages` the homepage uses.

## Conclusions

1. A marketplace file on `retran.me` or on `github.io` is a `url` marketplace,
   and whether `marketplace update` fetches it again is what a test settles
   first.
2. `meowshed/meowpaw` can't publish to a subdomain of `retran.me` while
   `retran.me` is verified for the owner's personal account.
3. A repository the owner's account owns can serve the file at
   `meow.retran.me` with one CNAME record at EuroDNS, or at `retran.me/<name>/`
   with none. Either way a workflow in `meowshed/meowpaw` has to tell it a
   release happened, which takes a token with access to that repository.
4. `meowshed.github.io/meowpaw/marketplace.json` can be deployed by the release
   workflow itself, with no token for another repository and no domain, and its
   address names the forge.
5. A person turns on auto-update for the marketplace once; without it, they run
   `claude plugin marketplace update meowpaw`.

## Sources

- [Plugin marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md),
  read 2026-09-26 - the input each marketplace source type is built from, and
  the `url` source downloading only its file.
- [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins.md),
  read 2026-09-26 - updating a marketplace and a plugin, and the auto-update
  defaults.
- [Plugin loading](https://code.claude.com/docs/en/plugins/loading.md), read
  2026-09-26 - when auto-update runs and which setting decides it.
- [About custom domains and GitHub Pages](https://github.com/github/docs/blob/main/content/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages.md),
  read 2026-09-26 - a user site's domain serving that account's project sites.
- [Verifying your custom domain for GitHub Pages](https://github.com/github/docs/blob/main/content/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages.md),
  read 2026-09-26 - which repositories may publish to a verified domain and its
  subdomains.
- [Managing a custom domain for your GitHub Pages site](https://github.com/github/docs/blob/main/content/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site.md),
  read 2026-09-26 - a custom subdomain set in the settings and a `CNAME`
  record, with no `CNAME` file for a workflow-deployed site.
- The GitHub API and DNS, 2026-09-26 - the Pages settings of
  `retran/retran.github.io` and `meowshed/meowpaw`, the homepage's deploy
  workflow, the records of `retran.me`, `www.retran.me` and `meow.retran.me`,
  and the zone's name servers.
