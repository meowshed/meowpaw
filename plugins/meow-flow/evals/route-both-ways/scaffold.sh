#!/bin/sh
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

# The route cases read the repository the unit ships in, so this copies its
# committed tree into the case's working directory. The runner calls it by
# its path in the case, so the tree is found from there. The copy is
# committed to a fresh repository, so each run starts where
# `git status --porcelain` prints nothing and a write shows in it.
set -eu
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
git -C "$root" archive HEAD | tar -x -f -
git init -q
git add -A
git -c user.name=scaffold -c user.email=scaffold@example.invalid \
  -c commit.gpgsign=false commit -q --no-verify -m scaffold
