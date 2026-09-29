#!/bin/sh
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

# Writes the draft decision and a repository agent that replaces the shipped
# reviewer and says nothing of an outcome, so its report carries no outcome
# line. A person runs it in an empty directory before the case.
set -eu
mkdir -p .claude/agents project/adrs
cat >.claude/agents/record-reviewer.md <<'AGENT'
---
name: record-reviewer
description: Reviews one project record and reports findings, editing nothing. Used only by the reviewer-with-no-outcome case.
tools: [Read, Grep, Glob]
maxTurns: 10
model: haiku
effort: low
omitClaudeMd: true
skills: []
---

<role>
You read the record at the path you are given and list anything missing from
it, one finding per line, and nothing else.
</role>
AGENT
cat >project/adrs/ADR-0100-cache-in-redis.md <<'RECORD'
---
id: ADR-0100
artifact: adr
status: draft
revised: 2026-09-20
addresses: [REQ-0100]
---

# 100. The session cache moves to Redis

## Decision

The session cache moves from the application process to Redis, because a
cache inside the process is lost on every deploy.

## What it costs

Operations runs one more service, a Redis instance, and is paged for it.
RECORD
