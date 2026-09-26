# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Check a commit message against the convention the repository declares.

SPC-1050 states the behaviour. The convention sits under `[commits]` in
`.meowpaw/profile.toml` (REQ-1290): the types with their release meaning
(REQ-1318), the subject limit (REQ-1302) and the trailers every message carries
(REQ-1308, REQ-1310). The attribution check runs whatever the profile says,
because the ban admits no exception (REQ-1294, REQ-1295). A message is never
reported as meeting a convention nobody declared (REQ-1314).
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

PROFILE = Path(".meowpaw") / "profile.toml"
DEFAULT_LIMIT = 72
MEANINGS = ("major", "minor", "patch", "none")
KEYS = ("types", "subject_limit", "trailers")

EXIT_MET, EXIT_VIOLATED, EXIT_USAGE, EXIT_UNDECLARED = 0, 1, 2, 3

SUBJECT = re.compile(r"^(?P<type>[a-z][a-z0-9-]*)(?:\((?P<scope>[^()\s]+)\))?(?P<bang>!)?: (?P<text>\S.*)$")
# The pattern, never a bare name: a path such as plugins/meow-core/ or the
# product a harness targets is not attribution.
ATTRIBUTION = re.compile(
    r"co-authored-by:.*\b(claude|anthropic|copilot|openai|chatgpt|gpt-?\d|gemini|codex|cursor|devin|aider)\b"
    r"|generated (with|by) \[?(claude|copilot|chatgpt|gemini|cursor|codex|an? ai)"
    r"|noreply@(anthropic|openai)\.com",
    re.IGNORECASE,
)


def repository_root():
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
        if top:
            return Path(top)
    except (OSError, subprocess.CalledProcessError):
        pass
    return Path.cwd()


def convention(root):
    """The declared convention, or why there is none, and what was ignored."""
    path = root / PROFILE
    result = {"state": "declared", "detail": None, "types": {}, "limit": DEFAULT_LIMIT,
              "trailers": [], "ignored": [], "malformed": []}
    if not path.is_file():
        result.update(state="undeclared", detail=f"{PROFILE} doesn't exist")
        return result
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        result.update(state="unparseable", detail=str(error))
        return result
    table = data.get("commits")
    if not isinstance(table, dict):
        result.update(state="undeclared", detail="the profile has no [commits] table")
        return result

    result["ignored"] = [f"commits.{key}" for key in table if key not in KEYS]
    types = table.get("types", {})
    if not isinstance(types, dict):
        result["malformed"].append("`types` isn't a table")
        types = {}
    for name, meaning in types.items():
        if meaning in MEANINGS:
            result["types"][name] = meaning
        else:
            result["malformed"].append(f"type `{name}` means {meaning!r}, not one of {', '.join(MEANINGS)}")
    limit = table.get("subject_limit", DEFAULT_LIMIT)
    if isinstance(limit, int) and not isinstance(limit, bool) and limit > 0:
        result["limit"] = limit
    else:
        result["malformed"].append("`subject_limit` isn't a positive whole number")
    trailers = table.get("trailers", [])
    if isinstance(trailers, list) and all(isinstance(t, str) for t in trailers):
        result["trailers"] = trailers
    else:
        result["malformed"].append("`trailers` isn't a list of names")
    return result


def report_convention(root):
    found = convention(root)
    if found["state"] != "declared":
        print(f"meow-scm convention: {found['state']} ({found['detail']})")
        return EXIT_UNDECLARED
    print(f"meow-scm convention, from {PROFILE}\n")
    for name, meaning in found["types"].items():
        print(f"type {name:<10} release: {meaning}")
    print(f"subject limit  {found['limit']} characters")
    print(f"trailers       {', '.join(found['trailers']) or 'none declared'}")
    for problem in found["malformed"]:
        print(f"malformed      {problem}")
    if found["ignored"]:
        print(f"\nNot read by meow-scm: {', '.join(found['ignored'])}")
    return EXIT_MET


def problems(message, found):
    """Every violation, as (line number, rule, detail)."""
    lines = [line for line in message.splitlines() if not line.startswith("#")]
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines or not lines[0].strip():
        return [(1, "empty message", "the message has no subject")]

    found_problems = []
    for number, line in enumerate(lines, start=1):
        if ATTRIBUTION.search(line):
            found_problems.append((number, "attribution", f'"{line.strip()}" credits a tool, an agent or a vendor'))
    if found["state"] != "declared":
        return found_problems

    subject = lines[0]
    match = SUBJECT.match(subject)
    if not match:
        found_problems.append((1, "subject form", "the subject isn't `type(scope)!: description`"))
    elif found["types"] and match["type"] not in found["types"]:
        declared = ", ".join(found["types"])
        found_problems.append((1, "declared type", f"`{match['type']}` isn't a declared type ({declared})"))
    if len(subject) > found["limit"]:
        found_problems.append((1, "subject length", f"{len(subject)} characters, over the limit of {found['limit']}"))
    if subject.rstrip().endswith("."):
        found_problems.append((1, "subject ending", "the subject ends in a full stop"))
    if len(lines) > 1 and lines[1].strip():
        found_problems.append((2, "blank line", "the body follows the subject with no empty line between them"))
    for trailer in found["trailers"]:
        if not any(re.match(rf"^{re.escape(trailer)}: \S", line) for line in lines[1:]):
            found_problems.append((len(lines), "trailer", f"the `{trailer}` trailer is missing"))
    return found_problems


def check_message(root, source):
    if source is None:
        message = sys.stdin.read()
    else:
        try:
            message = Path(source).read_text(encoding="utf-8")
        except OSError as error:
            print(f"meow-scm check-message: can't read {source}: {error.strerror}", file=sys.stderr)
            return EXIT_USAGE
    found = convention(root)
    listed = problems(message, found)
    for number, rule, detail in sorted(listed):
        print(f"line {number}: {rule}: {detail}")
    if found["state"] == "declared":
        for problem in found["malformed"]:
            print(f"convention: malformed: {problem}")
    if listed:
        print(f"meow-scm check-message: {len(listed)} problem{'s' if len(listed) != 1 else ''}; "
              "don't use this message until they are fixed")
        return EXIT_VIOLATED
    if found["state"] != "declared":
        print(f"meow-scm check-message: convention {found['state']} ({found['detail']}); "
              "only the attribution check ran, and it found nothing")
        return EXIT_UNDECLARED
    print("meow-scm check-message: the message meets the declared convention")
    return EXIT_MET


def main(argv):
    root = repository_root()
    if argv == ["convention"]:
        return report_convention(root)
    if argv[:1] == ["check-message"] and len(argv) <= 2:
        return check_message(root, argv[1] if len(argv) == 2 else None)
    print("usage: meow-scm convention | meow-scm check-message [FILE]", file=sys.stderr)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
