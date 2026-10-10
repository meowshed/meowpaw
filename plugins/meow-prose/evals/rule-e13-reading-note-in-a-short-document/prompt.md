---
name: rule-e13-reading-note-in-a-short-document
description: A text carrying a named defect.
tags: [defect, rule-E13]
runs: 3
max_turns: 10
---

Use the meow-prose:prose agent to review the text below, and print its report as it gives it.

<text>
# Backups

## How to read this document

This document has three sections. Read them in order. The first section describes the schedule, the second describes where backups go, and the third describes how to restore.

## Schedule

Backups run at 02:00 UTC.

## Location

They go to the `backups` bucket.

## Restore

Run `restore --latest`.
</text>
