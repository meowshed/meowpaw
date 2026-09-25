# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Resolve the five verbs from the repository's profile, report them, and run them.

SPC-1040 states the behaviour. A verb resolves only from the command the
repository declares under `[verbs]` in `.meowpaw/profile.toml` (REQ-0134), and
a verb that resolves to nothing is reported as unresolved and of which kind,
never as passed (REQ-0136, REQ-0154). `status` runs nothing (REQ-0150). `run`
records each verb's exact command, exit status and whole output (REQ-0144,
REQ-0156), and leads a failed verb with its last lines (REQ-0135).
"""

import json
import subprocess
import sys
import time
import tomllib
from pathlib import Path

VERBS = ("fmt", "lint", "typecheck", "test", "build")
PROFILE = Path(".meowpaw") / "profile.toml"
TAIL = 20

EXIT_PASSED, EXIT_FAILED, EXIT_USAGE, EXIT_UNRESOLVED = 0, 1, 2, 3


def repository_root():
    """The top of the working tree, or the current directory where there is none."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
        if top:
            return Path(top)
    except (OSError, subprocess.CalledProcessError):
        pass
    return Path.cwd()


def resolve(root):
    """The profile's state and, for each verb, what it resolves to or why it doesn't."""
    path = root / PROFILE
    report = {"profile": str(path), "profile_state": "present", "error": None,
              "verbs": {}, "ignored": []}

    def unresolved(kind, detail):
        return {"state": "unresolved", "kind": kind, "detail": detail}

    if not path.is_file():
        report.update(profile=None, profile_state="absent")
        for verb in VERBS:
            report["verbs"][verb] = unresolved("no profile", f"{PROFILE} doesn't exist")
        return report
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        report.update(profile_state="unparseable", error=str(error))
        for verb in VERBS:
            report["verbs"][verb] = unresolved("profile unparseable", str(error))
        return report

    report["ignored"] += [f"[{table}]" for table in data if table != "verbs"]
    declared = data.get("verbs", {})
    if not isinstance(declared, dict):
        for verb in VERBS:
            report["verbs"][verb] = unresolved("malformed declaration", "`verbs` isn't a table")
        return report
    report["ignored"] += [f"verbs.{key}" for key in declared if key not in VERBS]
    for verb in VERBS:
        if verb not in declared:
            report["verbs"][verb] = unresolved("undeclared", "the profile doesn't name it")
        elif not isinstance(declared[verb], str) or not declared[verb].strip():
            report["verbs"][verb] = unresolved("malformed declaration",
                                               "the value isn't one command")
        else:
            report["verbs"][verb] = {"state": "resolved", "command": declared[verb],
                                     "source": str(PROFILE)}
    return report


def status(root, as_json):
    report = resolve(root)
    if as_json:
        print(json.dumps(report, indent=2))
        return EXIT_PASSED
    where = report["profile"] or f"{root / PROFILE} (absent)"
    print(f"meow-verbs status, profile {where}\n")
    for verb, entry in report["verbs"].items():
        if entry["state"] == "resolved":
            print(f"{verb:<10} resolved    {entry['command']}   (from {entry['source']})")
        else:
            print(f"{verb:<10} unresolved  {entry['kind']}: {entry['detail']}")
    if report["ignored"]:
        print(f"\nNot read by meow-verbs: {', '.join(report['ignored'])}")
    return EXIT_PASSED


def run(root, names):
    if not names:
        print(f"meow-verbs run: name the verbs to run, from: {' '.join(VERBS)}", file=sys.stderr)
        return EXIT_USAGE
    unknown = [name for name in names if name not in VERBS]
    if unknown:
        print(f"meow-verbs run: {', '.join(unknown)} isn't a verb; the five are "
              f"{' '.join(VERBS)}", file=sys.stderr)
        return EXIT_USAGE

    report = resolve(root)
    outcomes = []
    for verb in names:
        entry = report["verbs"][verb]
        if entry["state"] != "resolved":
            print(f"== {verb}: unresolved ({entry['kind']}: {entry['detail']}), not run\n")
            outcomes.append((verb, "unresolved"))
            continue
        command = entry["command"]
        started = time.monotonic()
        done = subprocess.run(command, shell=True, cwd=root, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        seconds = time.monotonic() - started
        output = done.stdout.decode("utf-8", errors="replace")
        print(f"== {verb}: `{command}`")
        if done.returncode == 0:
            print(f"passed, exit status 0 after {seconds:.1f}s\n")
            outcomes.append((verb, "passed"))
        else:
            lines = output.rstrip("\n").splitlines()
            print(f"failed, exit status {done.returncode} after {seconds:.1f}s; "
                  f"the last {min(TAIL, len(lines))} lines of its output:")
            print("\n".join(lines[-TAIL:]))
            print()
            outcomes.append((verb, "failed"))
        print(f"-- whole output of {verb}:")
        print(output, end="" if output.endswith("\n") or not output else "\n")
        print(f"-- end of {verb}\n")

    print("summary: " + ", ".join(f"{verb} {result}" for verb, result in outcomes))
    results = {result for _, result in outcomes}
    if "failed" in results:
        return EXIT_FAILED
    if "unresolved" in results:
        return EXIT_UNRESOLVED
    return EXIT_PASSED


def main(argv):
    root = repository_root()
    if argv[:1] == ["status"] and argv[1:] in ([], ["--json"]):
        return status(root, argv[1:] == ["--json"])
    if argv[:1] == ["run"]:
        return run(root, argv[1:])
    print("usage: meow-verbs status [--json] | meow-verbs run <verb>...", file=sys.stderr)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
