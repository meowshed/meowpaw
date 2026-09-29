#!/bin/sh
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

# The route cases read the repository the unit ships in, so this copies its
# committed tree into the case's working directory. The runner calls it by
# its path in the case, so the tree is found from there.
set -eu
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
git -C "$root" archive HEAD | tar -x -f -
