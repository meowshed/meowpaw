---
id: RES-0142
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0026, RES-0005
---

# repomix

## Summary

A tool that packs a repository for a model is where its secrets are most likely
to leave it. What makes this one usable is that the secret scan is on by
default. So the pack never disables it and reports a repository that has.
Compression is lossy in a specific way: it keeps signatures and removes bodies.
So a finding about behaviour cannot come from a compressed pack, and the mode
is recorded with anything derived from it.

Research for one supported tool. repomix packs a repository into a single file
for a model to read. That makes it the harness's answer to _understand this
codebase you have never seen_, and the place where a repository's secrets are
most likely to leave it.

It covers what it produces, what it excludes and how reliably, what
compression costs, how it is configured, what the pack authors, and what the
skill has to contain.

It does not cover context gathering as a method question, which is
[RES-0026-memory.md](RES-0026-memory.md).

## The question

A tool that concatenates a repository is trivial. A tool a harness may point at
an unfamiliar repository is not. The output goes to a model, the model is a
third party, and the repository may contain credentials the person running the
harness has never looked at.

So the question is what guarantees this tool actually makes, and which of them
the harness may rely on.

## Method

We fetched and read the tool's documentation on 2026-09-20. The guide gave
output formats, ignore handling and splitting. The security page gave what the
scan detects and the two ways to disable it, and the compression page gave what
is kept and what is removed.

The security page states no limitations on the scan, and we record that absence
as an absence, treating it as no guarantee of completeness, which we decided
deliberately.

Nothing was installed or run, and no repository was packed.

## Findings

### What it produces, and why the format matters

repomix packs a repository into a single file in plain text, XML or Markdown,
and counts tokens against a model's context limit. It can pack a remote
repository without a local clone, watch a directory for changes, and run as an
MCP server so a model calls it directly.

`--split-output` divides a large result into several files, which is what makes
a repository larger than a context window usable at all.

The token count is the part a harness uses, and admiring it does nothing. A
packed repository that does not fit is not a smaller answer; it is a truncated
one, and knowing the count before sending it is the difference between a plan
and a surprise.

### The security check is on by default, and that default is the reason the tool is usable here

Secretlint runs over the files before packing, and _"Security checks are
enabled by default."_ It detects API keys, access tokens, credentials, private
keys, environment variables, cloud provider credentials, database connection
strings and authentication tokens.

Binary files are excluded from the output while their paths remain visible, and
`.gitignore` and `.git/info/exclude` are respected, with `.repomixignore` for
additional exclusions.

It can be turned off - `--no-security-check`, or `enableSecurityCheck: false`
in `repomix.config.json` - and that is the setting this method has a rule
about. A harness that disables the secret scan before sending a repository to a
model has removed the only automatic protection between a private key and a
third party. The pack never passes that flag and never writes that
configuration value, and if a repository's own configuration disables it, that
is reported and never silently accepted.

The documentation states no limitations on the check, which this document
records: absence of a stated limitation guarantees no completeness. A detector
works on patterns, and a credential that does not look like one is not
detected. So the check is treated as a filter that reduces risk and proves
nothing about what remains. The method's own prohibition continues to apply on
top of it: do not read, print or transmit a repository's secret material.

### Compression is lossy in a specific, useful way

`--compress` uses tree-sitter to keep function signatures, interface
definitions, class structures and type information, and to remove function
bodies, loop logic, conditional details and internal variable declarations. It
is off by default and is marked experimental.

That is exactly the right trade for one task and exactly wrong for another.
_What is the shape of this codebase_ is answered by signatures. _Why does this
function behave like this_ is not answerable from a compressed pack at all, and
a model given one will answer anyway.

So the pack states which mode produced the material it is reasoning from. A
finding derived from a compressed pack is a finding about structure, and citing
it as evidence about behaviour is citing something that was removed before the
model saw it.

Being marked experimental is a second reason to record the mode: the boundary
between kept and removed may move between versions, so a claim about what was
in the pack is version-specific.

### The exclusions are three mechanisms, and only one is the repository's

`.gitignore` and `.git/info/exclude` are the repository's and the user's
respectively; `.repomixignore` is the tool's own. A pack that needs to exclude
something for the harness's reasons writes the third and edits none of the
first, because the first is the project's file and has other readers.

### What the pack authors

`repomix.config.json` and `.repomixignore`.

It writes no `enableSecurityCheck: false`, and it adds no exclusion that hides
material a reviewer would want. A packed repository is a description of a
codebase, and an exclusion that quietly removes a directory produces a
description that is wrong, and not merely shorter.

### What a reviewer needs that no command reports

Whether the pack that a conclusion came from was compressed.

Whether the token count was checked before the pack was sent, or the result was
truncated.

Whether the security check was on, and whether the repository's own
configuration turned it off.

Whether an exclusion pattern is hiding something load-bearing.

### What the skill has to contain

In the body, in this order:

1. The security rule, first. The check is on by default, the pack never
   disables it, a repository that disables it is reported, and the check is a
   filter that proves nothing. 2. Mode is recorded. Compressed or not, and what
   compression removes. 3. Size before sending. Count tokens, and use
   `--split-output` where the pack would otherwise be truncated. 4. Which
   ignore file to write. `.repomixignore`, not the repository's. 5. What must
   never happen. Passing `--no-security-check`. Citing a compressed pack as
   evidence about behaviour. Sending a pack larger than the window. Excluding a
   directory without saying so.

In supporting files: the output formats and when each is right; the
configuration schema; what compression keeps and removes; and the dated facts
with what to re-check, since the compression boundary is experimental.

## Conclusions

1. The security check is left enabled, always, because it is the only automatic
   protection between a repository's credentials and a third party. 2. A
   repository configured to disable the check is reported, and never packed
   silently under its own setting. 3. The check is treated as a filter that
   proves nothing. It matches patterns, the documentation states no
   completeness guarantee, and the method's own prohibition on reading or
   transmitting secret material still applies. 4. The mode that produced a pack
   is recorded with any finding derived from it, because compression removes
   function bodies and a conclusion about behaviour cannot come from a pack
   that lacks them. 5. Compression is used for structural questions only, since
   signatures, interfaces, class structures and types are what it keeps. 6. A
   compressed pack's contents are version-specific, because the feature is
   marked experimental and the boundary between kept and removed may move. 7.
   The token count is checked before the pack is used, and `--split-output` is
   preferred to sending something that will be truncated. 8. Exclusions the
   harness needs go in `.repomixignore`, not in the repository's `.gitignore`,
   which has other readers. 9. An exclusion is disclosed, because a packed
   repository is a description and a quiet omission makes the description
   wrong, and not merely shorter. 10. Binary files are excluded while their
   paths remain, which is the correct default and is reported as part of what
   the pack contains. 11. The skill body carries the security rule, mode
   recording, size, which ignore file to write, and the prohibitions, in that
   order.

## Sources

All read 2026-09-20.

- [repomix guide](https://repomix.com/guide/) - packing a repository into a
  single file in plain text, XML or Markdown; token counting against context
  limits; respecting `.gitignore` and `.git/info/exclude` with `.repomixignore`
  for additional rules; remote repositories; watch mode; `--split-output`;
  `repomix.config.json`; the Secretlint security scan; and the MCP server
  integration. - [repomix security](https://repomix.com/guide/security) - that
  security checks are enabled by default; that Secretlint detects API keys,
  access tokens, credentials, private keys, environment variables, cloud
  credentials, database connection strings and authentication tokens; that
  binary files are excluded while their paths remain visible; and the two ways
  to disable the check, `--no-security-check` and `enableSecurityCheck: false`.
  The absence of any stated limitation is recorded as an absence, and it
  guarantees nothing. - [repomix code
  compression](https://repomix.com/guide/code-compress) - that `--compress`
  parses with tree-sitter and preserves function signatures, interface
  definitions, class structures and type information while removing function
  bodies, loop logic, conditional details and internal variable declarations;
  that it is off by default; and that it is marked experimental.
