# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The gate runs every check the verbs run, as REQ-1754 asks.

CI runs `mise run all`, and a contributor reproduces a failure by running the
verbs the profile declares. Where the two disagree, a defect the verbs catch
passes CI and reaches the trunk, as BUG-1500 and BUG-1510 did. This check
reads both declarations and fails naming the member the gate lacks.
"""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def members(command):
    """Each command one verb runs, splitting on `&&` at the top level."""
    return [part.strip() for part in command.split("&&") if part.strip()]


def covered(member, depends, runs):
    """Whether the gate runs the member: by task name, or by its exact command."""
    match = re.fullmatch(r"mise run ([\w-]+)", member)
    if match:
        return match.group(1) in depends, f"the task {match.group(1)}"
    for task in depends:
        if runs.get(task) == member:
            return True, f"the task {task}"
    return False, ""


def main():
    profile = tomllib.loads((ROOT / ".meowpaw" / "profile.toml").read_text(encoding="utf-8"))
    mise = tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))
    depends = mise["tasks"]["all"]["depends"]
    runs = {name: task.get("run", "") for name, task in mise["tasks"].items()}
    failures = []
    for verb, command in profile["verbs"].items():
        for member in members(command):
            ok, where = covered(member, depends, runs)
            if not ok:
                failures.append(f"the {verb} verb runs `{member}`, which no task the gate runs carries")
    for failure in failures:
        print(failure)
    print(f"{len(failures)} gate-coverage failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
