#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The method names no language (REQ-0070, REQ-0072, REQ-0084, ADR-2640).

What the harness tells a repository has to hold in every language, so no
prompt, template or page in the kernel, method and practice units names a
programming language, a framework, a build tool, a package manager or a source
file extension. The check reads the Markdown pages and the templates of those
units in both distributions and fails, naming the file, the line and the word,
on a word from its list.

Four things are never read: a pack, whose job is to know a language; a unit's
own program, which is written in some language (ADR-1070); a fenced block whose
info string names the pack whose output it shows; and the README of a Pi
package, which tells a person how to install the package through the Pi host's
own registry and so names that host's package manager. Every unit under
`plugins/` is in `READ` or in `PACKS`, so a new unit that joins neither fails
the check instead of escaping it. A run that reads no file fails, because a
check over nothing is no pass.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTRIBUTIONS = ("plugins", "packages")
# The kernel, method and practice units. ADR-2640 leaves the catalogue's layers
# to a later decision, so this list stands in for it, as KERNEL does in check_kernel.py.
READ = (
    "meow-core", "meow-flow", "meow-scm", "meow-prose", "meow-author", "meow-code",
    "meow-checks", "meow-licence", "meow-loop", "meow-prose-gate", "meow-unattended",
)
PACKS = (
    "meow-git", "meow-github", "meow-mise", "meow-gotask", "meow-markdown",
    "meow-rust", "meow-go", "meow-python", "meow-typescript", "meow-csharp",
    "meow-lua", "meow-godot", "meow-starlark", "meow-scheme",
)
# A unit's program and its measurement cases are not prompts, templates or pages.
SKIPPED = ("bin", "hooks", "tests", "evals", "extensions", "node_modules", "__pycache__")

# Matched in any case: no sentence uses these for anything else.
INSENSITIVE = (
    r"rust|rustc|rustfmt|cargo|clippy|python3?|pytest|pip|pipenv|poetry|conda|mypy|pyright|ruff|django|flask"
    r"|javascript|typescript|node\.js|nodejs|npm|npx|yarn|pnpm|webpack|vite|vitest|jest|eslint|tsc|deno"
    r"|golang|gofmt|golangci-lint|kotlin|scala|haskell|elixir|erlang|clojure|perl|php|rails"
    r"|dotnet|msbuild|nuget|c#|c\+\+|\.net|gradle|maven|mvn|cmake|bazel|buck2?|buildifier|javac|gcc|clang"
    r"|lua|luarocks|gdscript|godot|racket|raco|neovim|angular|vue|svelte"
)
# Matched with their capital only, because each is also an ordinary word in lower
# case; the lookahead drops the verb uses at a sentence start.
SENSITIVE = {
    "Go": r"(?! to\b| on\b| back\b| through\b| ahead\b| and\b)",
    "Scheme": "",
    "Swift": "",
    "Ruby": "",
    "Java": "",
    "Dart": "",
    "Zig": "",
    "Elm": "",
    "React": r"(?! to\b| when\b| with\b)",
}
# A file named by its extension: `main.rs`, or the bare `*.py`.
EXTENSIONS = r"py|rs|ts|tsx|js|jsx|mjs|go|cs|java|rb|lua|c|cc|cpp|h|hpp|kt|swift|php|gd|sh|bash"

INSENSITIVE_RE = re.compile(r"(?<![\w-])(?:" + INSENSITIVE + r")(?![\w-])", re.IGNORECASE)
SENSITIVE_RE = re.compile(r"(?<![\w-])(?:" + "|".join(w + after for w, after in SENSITIVE.items()) + r")(?![\w-])")
EXTENSION_RE = re.compile(
    r"(?<=[\w*])\.(?:" + EXTENSIONS + r")(?![\w-])|(?<![\w.])\.(?:" + EXTENSIONS + r")(?![\w-])",
    re.IGNORECASE,
)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
UNIT_NAME = re.compile(r"meow-[a-z]+(?:-[a-z]+)*")


def is_prompt(unit: Path, path: Path) -> bool:
    parts = path.relative_to(unit).parts
    if unit.parent.name == "packages" and parts == ("README.md",):
        return False
    if any(part in SKIPPED for part in parts[:-1]):
        return False
    return path.suffix == ".md" or parts[0] in ("templates", "prompts")


def words(line: str) -> list[str]:
    return [m.group(0) for r in (INSENSITIVE_RE, SENSITIVE_RE, EXTENSION_RE) for m in r.finditer(line)]


def names_a_pack(info: str, packs: tuple[str, ...]) -> bool:
    return any(name in packs for name in UNIT_NAME.findall(info))


def findings_in(path: Path, packs: tuple[str, ...]) -> list[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    out, fence, exempt = [], None, False
    for number, line in enumerate(text.splitlines(), start=1):
        marker = FENCE.match(line)
        if fence is None and marker:
            fence, exempt = marker.group(1)[0] * len(marker.group(1)), names_a_pack(marker.group(2), packs)
            continue
        if fence is not None:
            if marker and marker.group(1).startswith(fence) and not marker.group(2).strip():
                fence = None
                continue
            if exempt:
                continue
        out.extend((number, word) for word in words(line))
    return out


def main(root: Path = ROOT, read: tuple[str, ...] = READ, packs: tuple[str, ...] = PACKS) -> int:
    failures, checked = [], 0
    plugins = root / "plugins"
    if plugins.is_dir():
        for unit in sorted(p.name for p in plugins.iterdir() if p.is_dir()):
            if unit not in read and unit not in packs:
                failures.append(f"plugins/{unit}: in neither READ nor PACKS of tools/check_language.py")
    for distribution in DISTRIBUTIONS:
        for name in read:
            unit = root / distribution / name
            if not unit.is_dir():
                continue
            for path in sorted(unit.rglob("*")):
                if not path.is_file() or not is_prompt(unit, path):
                    continue
                checked += 1
                for number, word in findings_in(path, packs):
                    failures.append(f"{path.relative_to(root)}:{number}: names {word}")
    for line in failures:
        print(line)
    print(f"{checked} method files read, {len(failures)} findings")
    if checked == 0:
        print("no file read, so the check proves nothing")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
