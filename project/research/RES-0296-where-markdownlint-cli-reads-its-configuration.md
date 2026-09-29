---
id: RES-0296
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0295
---

# Where markdownlint-cli reads its configuration, as observed

## Summary

markdownlint-cli 0.49.1 applies a file named as `--config=<path>`, as it does
one named by `--config <path>` or `-c <path>`, and it reads `-c=<path>` as a
file whose name starts with `=`, so it fails to read it and runs its default
rules. Run from the root, it ignores a `.markdownlint.json` in `docs/`, as
RES-0295 saw it ignore a `.markdownlintrc` there. This adds two observations
to RES-0295 on markdownlint-cli alone.

## The question

A pack that reports markdownlint-cli running on its defaults has to accept
every form of the flag that names a configuration, or it reports a finding
the tool doesn't have. RES-0295 tried `-c <path>` and `--config <path>` and
left out the joined forms, and it tried no nested `.markdownlint.*` file.

## Method

I ran markdownlint-cli 0.49.1 on 2026-09-29 on this machine, a Mac on arm64,
through `mise exec npm:markdownlint-cli@0.49.1`, in scratch directories
outside any repository. Each fixture held `README.md` and `docs/b.md`, each
with a 149-character line, and a configuration disabled rule MD013 with
`{ "MD013": false }`. Each run passed the glob `'**/*.md'`.

## Findings

### markdownlint-cli applies `--config=<path>` and misreads `-c=<path>`

With `--config=.config/mdl.json`, markdownlint-cli reported no MD013 line and
exited 0. With `-c=.config/mdl.json`, it printed
`Cannot read or parse config file '=.config/mdl.json': ENOENT: no such file or directory`,
then reported MD013 on both files.

### markdownlint-cli ignores a nested `.markdownlint.json`

With `.markdownlint.json` in `docs/` and markdownlint-cli run from the root,
it reported MD013 on `README.md` and on `docs/b.md`, and exited 1.

## Conclusions

1. A markdownlint-cli command names its configuration with `-c <path>`,
   `--config <path>` or `--config=<path>`. A `-c=<path>` word names none that
   exists, and the run goes on with the defaults.
2. markdownlint-cli run from the root takes no rule from a `.markdownlint.*`
   file below it, so only a file at the root configures a lint verb that runs
   it there.

## Sources

- markdownlint-cli 0.49.1, run on this machine on 2026-09-29 - that it
  applied `--config=<path>`, failed to read `-c=<path>`, and ignored a
  `.markdownlint.json` in `docs/` when run from the root.
