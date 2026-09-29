#!/bin/sh
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

# The fixture agent has a ceiling of two turns, and the twelve notes need
# twelve reads, so the agent reaches its ceiling before it can answer.
set -eu
mkdir -p .claude/agents notes
cat >.claude/agents/ceiling-probe.md <<'AGENT'
---
name: ceiling-probe
description: Reads the notes one at a time and reports the number each holds. Used only by the stopped-at-the-ceiling case.
maxTurns: 2
tools: Read, Glob
model: haiku
effort: low
omitClaudeMd: true
skills: []
---

<role>
You read each file you are given, one Read call per file, and never read two
files in one turn. Reply only once you have read every file.
</role>
AGENT
for n in 01 02 03 04 05 06 07 08 09 10 11 12; do
  echo "$n" >"notes/note-$n.txt"
done
