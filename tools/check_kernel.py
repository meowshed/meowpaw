#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The kernel names no unit outside it.

The kernel has to behave the same whether or not an optional unit is installed
(REQ-0077, ADR-1060), so no file it ships names another plugin. The check reads
every file in each kernel unit, except its measurement cases and results, which
are not shipped behaviour, and fails on the name of any other directory in
`plugins/`, naming the file and the line.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
KERNEL = ("meow-core",)


def main() -> int:
    others = sorted(p.name for p in PLUGINS.iterdir() if p.is_dir() and p.name not in KERNEL)
    if not others:
        print("no unit outside the kernel, nothing to check")
        return 0
    name = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, others)) + r")(?![\w-])")
    failures, checked = [], 0
    for unit in KERNEL:
        for path in sorted((PLUGINS / unit).rglob("*")):
            if not path.is_file() or "evals" in path.relative_to(PLUGINS / unit).parts:
                continue
            checked += 1
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                for match in name.finditer(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}: names {match.group(1)}, outside the kernel")
    for line in failures:
        print(line)
    print(f"{checked} kernel files, {len(failures)} names outside the kernel")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
