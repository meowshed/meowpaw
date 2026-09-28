---
id: RES-0294
artifact: research
status: approved
revised: 2026-09-28
elaborates: RES-0111
---

# The Markdown toolchain, as observed

## Summary

lychee 0.24.2 reports an unreachable link and a broken one with the same exit
status, 2, so only its JSON output tells a site that is down from a link that
is wrong. Its JSON does tell them apart: a timeout sits in its own map, a
failed lookup or a refused connection carries no status code, a missing
relative file carries a `file://` address, and a rejected response carries its
code. lychee reads `lychee.toml` from the directory it runs in, applies
`offline`, `max_retries` and `cache` from that file, rejects an unknown key
with exit status 3, and writes `.lycheecache` into the same directory when the
cache is on. It ignored a `lychee.toml` in a parent directory and an
`LYCHEE_OFFLINE` variable in the environment. On the markdownlint side, markdownlint-cli 0.49.1 ignores
a `.markdownlint-cli2.yaml` or `.markdownlint-cli2.jsonc` and runs its
defaults, and markdownlint-cli2 0.23.2 runs its defaults in silence where no
configuration exists. Where a directory holds a `.markdownlint.*` file and a
`.markdownlint-cli2.*` file that both set a rule, markdownlint-cli2 applied the
`.markdownlint.*` file in each of the five pairings I tried, and said nothing
about the other.

Research for the Markdown pack. It adds observations to
[RES-0111-markdown.md](RES-0111-markdown.md), which read the documentation and
ran nothing. It covers the link checker and the structural linter, and leaves
out the formatter, the prose linter, the spell checkers and the site
generators.

## The question

A pack that reports an unreachable link as unreachable, and a missing
configuration as a finding, has to know what the tools print in each case.
RES-0111 says lychee checks links and that markdownlint-cli ignores the newer
tool's commented configuration, but it ran neither. The question is what a
program can read from each tool's output and configuration, and which of those
cases the tools already report on their own.

## Method

I ran the tools on 2026-09-28 on this machine, a Mac on arm64, in scratch
directories outside any repository:

- lychee 0.24.2, fetched with `mise exec lychee@latest`;
- markdownlint-cli2 0.23.2, on markdownlint 0.41.1, as installed through mise;
- markdownlint-cli 0.49.1, run with `npx -y markdownlint-cli@0.49.1`.

The link fixtures named `https://httpbin.org/status/<code>` for 403, 404, 410,
429 and 503, a host under a domain nobody registered, `http://127.0.0.1:1/`
for a refused connection, `http://10.255.255.1/` for a timeout,
`https://expired.badssl.com/` for an expired certificate, and a relative link
to a file that doesn't exist. Each run passed `--format json --no-progress`,
with `--max-retries 0` and a short `--timeout` so no case waited on retries.
I didn't record the first run's timeout value, so I repeated the timeout case
the same day with `--timeout 2`, and it timed out after about 2.2 seconds with
the same JSON entry. The network answers depend on those third-party hosts on the day, so a repeat
can differ.

The lint fixtures held one Markdown file with a 92-character line and a
configuration setting rule MD013's `line_length` to a number other than the
default 80, so the reported limit shows which configuration the tool applied.

## Findings

### lychee exits 2 for an unreachable link exactly as for a broken one

A run whose only failure was a timeout exited 2, the same status a 404 and a
missing file gave, and a clean run exited 0. So a gate that reads lychee's exit
status reports a site that is down as a failed check of the document, which is
the conflation RES-0111's section on links warns about.

### The JSON output separates the cases a program needs

`--format json` printed one object with counts (`total`, `successful`,
`errors`, `timeouts`, `excludes` and more) and one map per outcome, each keyed
by the input file. Every entry held `url`, `status`, `span` with a line and a
column, and `duration`. The status told the cases apart:

| Case                                  | Where it appeared | `status.code` | `status.details` or text                                |
| ------------------------------------- | ----------------- | ------------- | ------------------------------------------------------- |
| Timeout                               | `timeout_map`     | none          | `Request timed out`                                     |
| Unregistered host                     | `error_map`       | none          | `Connection failed. Check network connectivity ...`     |
| Refused connection                    | `error_map`       | none          | `Connection refused - server may be down ...`           |
| Expired certificate                   | `error_map`       | none          | `SSL certificate expired. Site needs to renew ...`      |
| Relative link to a missing file       | `error_map`       | none          | `File not found. ...`, with a `file://` address         |
| 403, 404, 410, 429 and 503 responses  | `error_map`       | the code      | `Rejected status code: <code> <reason>`                 |
| `example.com` and a `.invalid` domain | `excluded_map`    | none          | `Excluded`, by lychee's default exclusions, not checked |

A failed DNS lookup and a refused connection both carried no status code, and
only their `details` text differed. No fixture made a connection fail any other
way, so I can't say how such a failure reads. A 429 came
with a hint on standard error about per-host concurrency, and nothing in the
JSON marked it apart from other rejected codes.

An address lychee excludes is never checked and sits in `excluded_map`, which
covers lychee's default exclusions and every remote address under `offline`.
A run whose only links were excluded exited 0, and a run with `--offline`
listed each remote address there with the detail
`This is due to your 'exclude' values`.

A run naming an input file that doesn't exist exited 1, printed
`Error: Cannot parse inputs from arguments` on standard error and nothing on
standard output. So an exit status of 1 means lychee checked nothing, and its
output isn't JSON.

### lychee reads `lychee.toml` from where it runs, and the file governs the run

With `offline = true`, `max_retries = 2`, `cache = true` and
`max_cache_age = "1d"` in `lychee.toml`, a run with no flags skipped every
remote link as excluded and still reported the missing relative file. `--help`
names `lychee.toml` as the default of `--config`, and gives the defaults a
repository gets when it declares nothing: 3 retries, `max_cache_age` of 1d,
and `offline` and `cache` off. A key spelled wrong, `offlin`, made lychee exit
3 with `Error while loading config`, so a misspelt declaration fails loudly and
never reads as absent.

lychee took its settings from nowhere else I could find. Run from a
subdirectory, it ignored an `offline = true` in the parent's `lychee.toml` and
checked the remote links. With `LYCHEE_OFFLINE=true` in the environment and no
file, it checked them too, and `--help` names no environment variable. `--help`
gives `--offline`, `--cache` and `--accept-timeouts` an optional value,
`[=<false|true>]`, and a run with `--offline --max-retries 0 --cache=false`
exited on the missing relative file alone and wrote no `.lycheecache`.

With `cache = true`, lychee wrote `.lycheecache` into the directory it ran in.
A repository that turns the cache on gets a file in its work tree after every
link check.

### markdownlint-cli ignores a markdownlint-cli2 configuration and runs its defaults

With a `.markdownlint-cli2.yaml` setting `line_length` to 20, markdownlint-cli2
reported the line against 20, and markdownlint-cli 0.49.1 reported it against
the default 80. A `.markdownlint-cli2.jsonc` setting 20 gave the same result
from markdownlint-cli. markdownlint-cli printed nothing about the file it
ignored. It
did read a `.markdownlint.jsonc` holding a comment, so RES-0111's warning holds
for the newer tool's own file names, and not for the commented JSON form as
such.

### markdownlint-cli2 runs its defaults in silence where no configuration exists

With no configuration file, markdownlint-cli2 printed `Finding: a.md`, the
count and each finding against the default limit, and no line saying no
configuration was found. Its output reads the same whether the repository
configured the rule set or never did.

### Two configurations in one directory, and markdownlint-cli2 applied one without saying so

A directory holding `.markdownlint.jsonc` with `line_length` 30 and
`.markdownlint-cli2.yaml` with a `config` setting 25 got its line reported
against 30. markdownlint-cli2 named neither file. A person who edits the
second file sees no effect and no reason.

I repeated this with four more pairings, each setting 30 in the
`.markdownlint.*` file and 25 in the `.markdownlint-cli2.*` file:
`.markdownlint.yaml` with `.markdownlint-cli2.jsonc`, `.markdownlint.jsonc`
with `.markdownlint-cli2.jsonc`, `.markdownlint.yaml` with
`.markdownlint-cli2.yaml`, and `.markdownlint.json` with
`.markdownlint-cli2.cjs`. Each reported the line against 30.

## Conclusions

1. A pack reporting a link check classifies each result from lychee's JSON
   output and never from its exit status, because lychee exits 2 for a timeout
   exactly as for a broken link.
2. A timeout, a failed or refused connection and a certificate error are
   reported as unreachable, with lychee's own detail, because each names a
   source outside the repository. This costs something: a misspelt host is
   reported as unreachable too, although it's a wrong link in the document.
   In these runs the failed lookup and the refused connection carried
   different `details` text and no code, so a pack could separate them only
   by matching that text, which conclusion 12 says carries no stability
   promise, or by a lookup of its own.
3. A relative link to a missing file is a finding about the document, because
   its target is in the repository.
4. A rejected response is classified by its code, because the JSON carries the
   code and nothing else marks a rate limit or a server error apart. Of the
   codes observed, 404 and 410 are findings about the document, because the
   server said the page is gone. 429 and 503 are unreachable, because the
   checker was throttled or the server failed, and the page may be fine. 403
   is left to the decision, because it can mean a server refusing the checker
   or a page hidden after deletion, and the JSON doesn't say which.
5. A link checker's offline behaviour, retries and cache are read from
   `lychee.toml` in the directory the check runs from, or the file `--config`
   names (per `--help`, not run), and from the flags the command passes. Those are the places lychee
   took them from in these runs: it ignored a parent directory's file and
   `LYCHEE_OFFLINE`. A key absent from all of them means lychee's default
   applies unseen.
6. A lychee exit status of 3 reports a configuration lychee rejected, and an
   exit status of 1 reports inputs it couldn't read. In both lychee checked
   nothing, so neither is a link finding.
7. An excluded address is neither a finding nor a pass of that address,
   because lychee never checked it, and lychee itself exits 0 on a run with
   only excluded addresses.
8. A cache turned on writes `.lycheecache` into the work tree, so a repository
   that declares one gets a file it didn't write.
9. A lint verb running markdownlint-cli beside a `.markdownlint-cli2.*` file
   runs with that file ignored, and nothing in the tool's output says so. I
   observed the `.yaml` and `.jsonc` forms. The other forms are inferred,
   because markdownlint-cli knows none of the `.markdownlint-cli2.*` names.
10. A lint verb running markdownlint-cli2 with no configuration file runs the
    default rule set, and nothing in the tool's output says so.
11. Where one directory holds a `.markdownlint.*` and a `.markdownlint-cli2.*`
    that both set a rule, markdownlint-cli2 applies the `.markdownlint.*` file,
    and nothing in the tool's output says so. Five pairings of the two
    families showed this. Two files of one family in one directory weren't
    tried.
12. Reading lychee's JSON ties a pack to the lychee it was observed against.
    The map names `timeout_map`, `error_map` and `excluded_map` and the
    `details` text carry no stability promise in anything this record read,
    and all of it was seen on 0.24.2 alone. lychee's `--help` documents no
    exit status as a contract either, so the exit status is only the
    interface a pack depends on least, and the JSON the one that tells the
    cases apart. Output a pack can't parse therefore means a broken tool,
    never a pass.

## Sources

- lychee 0.24.2, run on this machine on 2026-09-28, and its `--help` output
  that day - the JSON shape, the exit statuses 0, 1, 2 and 3, the defaults for
  retries, cache and offline, `lychee.toml` as the default configuration, the
  optional values of `--cache` and `--offline`, the excluded addresses, and
  the `.lycheecache` file. The `--help` text names no exit status other than
  the 0 that `--accept-timeouts` returns.
- markdownlint-cli2 0.23.2, run 2026-09-28 on this machine, on markdownlint
  0.41.1 - which configuration it applied in each of five pairings, and its
  silence where none existed or two did.
- markdownlint-cli 0.49.1, run through `npx` on 2026-09-28 - that it ignored a
  `.markdownlint-cli2.yaml` and a `.markdownlint-cli2.jsonc`, and read a
  commented `.markdownlint.jsonc`.
- [httpbin](https://httpbin.org/), read 2026-09-28 - the status codes the
  fixtures requested.
- [badssl.com](https://badssl.com/), read 2026-09-28 - the host serving an
  expired certificate.
