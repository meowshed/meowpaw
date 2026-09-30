#!/bin/sh
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

# A person runs this case, never the loop, because it needs a session with
# nobody in it and a deny rule. From an empty directory, run this script, then
# give the text of prompt.md to:
#
#   claude -p --permission-prompts none --plugin-dir <plugins/meow-prose> \
#     --output-format stream-json --verbose
#
# and read the stream against expected.md. The page's text is never in the
# prompt, so the agent has to read the path, and the deny rule refuses that.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p docs .claude
cp "$here/settings.json" .claude/settings.json
cat >docs/page.md <<'PAGE'
# Importing records

The importer leverages a robust pipeline to seamlessly transform records,
which is crucial for the monthly report.
PAGE
git init -q
git add -A
git -c user.name=scaffold -c user.email=scaffold@example.invalid \
  -c commit.gpgsign=false commit -q --no-verify -m scaffold
