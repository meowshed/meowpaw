#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Writes each unit's launcher and Pi extension from one template (REQ-4620, REQ-4510).

A unit's launcher and its package's launcher share one skeleton per host, and
the facts that differ per unit (its subcommand, the comment saying what the
launcher does without a binary, the lines it runs before the binary, and the
fallback it prints) are declared in `tools/launchers.toml`. A package extension
that only puts the launcher on PATH is the same file for every unit, so it has
no facts. The generator lives in `tools/` because a unit's file may not run a
path outside its own directory and the kernel may not name a unit.

    python3 tools/generate_launchers.py          # write the files
    python3 tools/generate_launchers.py --check  # fail naming each file that differs
"""

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS = Path(__file__).resolve().parent / "launchers.toml"

HEADER = """#!/bin/sh
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

# Runs this unit's binary of the native tool for this machine (SPC-1080).
@COMMENT@

case $0 in
*/*) here=${0%/*} ;;
*) here=$(command -v "$0") && here=${here%/*} ;;
esac
system='' cpu='' exe=''
case $(uname -s 2>/dev/null) in
Darwin) system=apple-darwin ;;
Linux) system=unknown-linux-musl ;;
MINGW* | MSYS* | CYGWIN*) system=pc-windows-msvc exe=.exe ;;
esac
case $(uname -m 2>/dev/null) in
arm64 | aarch64) cpu=aarch64 ;;
x86_64 | amd64) cpu=x86_64 ;;
esac
binary="$here/$cpu-$system/paw$exe"
"""

CLAUDE_FIND = """# The shared binary the core unit ships, found through the core unit's data
# directory, which the platform documents and the core unit's session start
# writes (REQ-4504). The unit's own build beside it is the fallback.
data=${CLAUDE_PLUGIN_DATA:+${CLAUDE_PLUGIN_DATA%/*}}
for core in "${data:-$HOME/.claude/plugins/data}"/meow-core-*/meow-root; do
  [ -f "$core" ] || continue
  read -r root <"$core" 2>/dev/null
  if [ -n "$root" ] && [ -f "$root/bin/$cpu-$system/paw$exe" ]; then
    binary="$root/bin/$cpu-$system/paw$exe"
    break
  fi
done
# Loaded in place from a checkout, the core unit sits beside this one.
[ -f "$binary" ] || {
  beside="$here/../../meow-core/bin/$cpu-$system/paw$exe"
  [ -f "$beside" ] && binary=$beside
}
# The platform version this unit was tested on, from its requires.toml
# (REQ-1738): on an older one the launcher stops here without running the
# binary, because the unit's behaviour was never seen on it. The version the
# platform reports comes from `claude --version`, which the platform's CLI
# reference documents.
required=$(sed -n 's/^claude_code *= *"\\([^"]*\\)".*/\\1/p' "$here/../requires.toml" 2>/dev/null)
if [ -n "$required" ]; then
  reported=$(claude --version 2>/dev/null | sed 's/^\\([0-9][0-9]*\\.[0-9][0-9]*\\.[0-9][0-9]*\\).*/\\1/')
  if [ -z "$reported" ]; then
    echo "paw: the platform's version is unknown, and this unit was tested on claude $required; it runs anyway" >&2
  else
    o1=$(printf '%s\\n' "$reported" | cut -d. -f1)
    o2=$(printf '%s\\n' "$reported" | cut -d. -f2)
    o3=$(printf '%s\\n' "$reported" | cut -d. -f3)
    n1=$(printf '%s\\n' "$required" | cut -d. -f1)
    n2=$(printf '%s\\n' "$required" | cut -d. -f2)
    n3=$(printf '%s\\n' "$required" | cut -d. -f3)
    if [ "${o1:-0}" -lt "${n1:-0}" ] || { [ "${o1:-0}" -eq "${n1:-0}" ] && [ "${o2:-0}" -lt "${n2:-0}" ]; } ||
      { [ "${o1:-0}" -eq "${n1:-0}" ] && [ "${o2:-0}" -eq "${n2:-0}" ] && [ "${o3:-0}" -lt "${n3:-0}" ]; }; then
      echo "paw: the platform reports claude $reported, and this unit was tested on claude $required, so it stops: install claude $required or later" >&2
      exit 3
    fi
  fi
fi
"""

CLAUDE_RUN = """if [ -n "$system" ] && [ -n "$cpu" ] && [ -f "$binary" ]; then
  [ -x "$binary" ] || chmod +x "$binary" 2>/dev/null
@PROLOGUE@  exec "$binary" @SUBCOMMAND@ "$@"
fi

"""

PI_RUN = """if [ -n "$system" ] && [ -n "$cpu" ] && [ -f "$binary" ]; then
  [ -x "$binary" ] || chmod +x "$binary" 2>/dev/null
@PROLOGUE@  exec "$binary" @SUBCOMMAND@ "$@"
fi

# The core extension exports the shared executable path for this wrapper.
if [ -n "${MEOWPAW_BINARY:-}" ] && [ -x "$MEOWPAW_BINARY" ]; then
@PROLOGUE@  exec "$MEOWPAW_BINARY" @SUBCOMMAND@ "$@"
fi

"""

REASON = (
    'reason="no paw executable was found for this machine, $(uname -s 2>/dev/null) on $(uname -m 2>/dev/null); '
    "@ADVICE@ for macOS, Linux and Windows on arm64 and x86_64\"\n"
)
ADVICE = {
    "claude": "install meow-core, which ships the shared binary",
    "pi": "reinstall the unit, which ships one",
}

STANDARD_TAIL = """case "$1" in
@COMMANDS@)
  echo "@NAME@ $1: @STATE@: $reason"
  exit 3
  ;;
*)
  echo "usage: @USAGE@" >&2
  exit 2
  ;;
esac
"""

EXTENSION = """// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * Pi extension for this unit.
 *
 * Puts the package's launcher on PATH so the skills call it by name, the
 * way Claude Code does natively for a plugin's bin/. The paw executable comes
 * from the core package's install (REQ-4612).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");

export default function (_pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;
}
"""


def host_facts(unit: dict, host: str) -> dict:
    """The unit's facts for one host: the shared table, overridden by the host's own."""
    return {**{k: v for k, v in unit.items() if k not in ("claude", "pi", "file")}, **unit.get(host, {})}


def launcher(name: str, unit: dict, host: str) -> str:
    """The launcher text for one unit on one host ("claude" or "pi"); `name` is the launcher's file name."""
    facts = host_facts(unit, host)
    comment = "\n".join("# " + line for line in facts["comment"])
    text = HEADER.replace("@COMMENT@", comment)
    run = CLAUDE_RUN if host == "claude" else PI_RUN
    if host == "claude":
        text += CLAUDE_FIND
    prologue = facts.get("prologue", "")
    text += run.replace("@PROLOGUE@", prologue).replace("@SUBCOMMAND@", facts["subcommand"])
    reason = REASON.replace("@ADVICE@", ADVICE[host])
    if "tail" in facts:
        tail = facts["tail"].replace("@REASON@\n", reason).replace("@REASON@", reason.rstrip("\n"))
    else:
        tail = reason + (
            STANDARD_TAIL.replace("@COMMANDS@", facts["commands"])
            .replace("@NAME@", name)
            .replace("@STATE@", facts["state"])
            .replace("@USAGE@", facts["usage"])
        )
    return text + tail.rstrip("\n") + "\n"


def expected(root: Path = ROOT, facts: Path = FACTS) -> dict[Path, str]:
    """Every file the generator writes, keyed by its path under `root`."""
    table = tomllib.loads(facts.read_text(encoding="utf-8"))
    files: dict[Path, str] = {}
    for name, unit in table["launcher"].items():
        file = unit.get("file", name)
        files[root / "plugins" / name / "bin" / file] = launcher(file, unit, "claude")
        files[root / "packages" / name / "bin" / file] = launcher(file, unit, "pi")
    for name in table["extension"]["units"]:
        files[root / "packages" / name / "extensions" / "bin.ts"] = EXTENSION
    return files


def differing(root: Path = ROOT, facts: Path = FACTS) -> list[Path]:
    """The generated files whose committed text differs, or that are missing."""
    out = []
    for path, text in expected(root, facts).items():
        try:
            same = path.read_text(encoding="utf-8") == text
        except OSError:
            same = False
        if not same:
            out.append(path)
    return out


def main(argv: list[str]) -> int:
    if "--check" in argv:
        bad = differing()
        for path in bad:
            print(f"{path.relative_to(ROOT)}: differs from what tools/generate_launchers.py writes")
        if bad:
            return 1
        print(f"{len(expected())} generated files equal their template")
        return 0
    for path, text in expected().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        if path.parent.name == "bin":
            path.chmod(0o755)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
