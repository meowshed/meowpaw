#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The hand-run case TSK-4950 criterion 3 asks for (REQ-0818, REQ-0824): a session holding delegated work
dispatches its review to a fresh agent and never a fork, and sends a disagreement between the implementer and
the reviewer to a third fresh agent given both positions and the brief. It runs each case on each model, once
by default, reads the session's dispatches from its stream and prints what each run did, then a tally. It exits
1 on any run that went other than the case wants. Every run calls a model, so no gate or workflow runs this:

    python3 plugins/meow-flow/evals/delegation.py [runs] [model...]

The models default to `sonnet` and `opus`, the two the prompts are measured on.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BRIEF_MARK = "MUST copy a constraint as it stands"
BRIEF = f"""agent: general-purpose
task: TSK-0001, authorised by EPC-0001

# What to build

from TSK-0001, What to do
```text
Add a `--quiet` flag to the report command that prints nothing on success.
```

# Constraints

from REQ-0001
```text
The report command {BRIEF_MARK}, with every clause kept.
```
"""
DIFF = """--- a/report.txt
+++ b/report.txt
@@ -1 +1,2 @@
 report prints its summary
+report --quiet prints nothing on success
"""
IMPLEMENTER_MARK = "must still print a failure"
REVIEWER_MARK = "must print nothing at all"
IMPLEMENTER = f"The implementer holds that a quiet run {IMPLEMENTER_MARK}."
REVIEWER = f"The reviewer holds that a quiet run {REVIEWER_MARK}."
FRAME = ("Load the `meow-flow:method` skill and read its implement step, `steps/implement.md`, in particular its "
         "rules for delegated work. A delegated agent implemented task TSK-0001 in this repository from the brief "
         "below, and its difference is below too. Act as that step says for the point described here, and do "
         "nothing else.\n\nThe brief:\n\n" + BRIEF + "\nThe difference:\n\n```diff\n" + DIFF + "```\n")
CASES = [
    ("review", FRAME + "\nThe delegated agent reported `outcome: DONE`. Have its work reviewed."),
    ("disagreement", FRAME + f"\nThe work was reviewed and the two disagree. {IMPLEMENTER} {REVIEWER} Settle it."),
]


def dispatches(stream):
    """Each Agent call the session made, as its input."""
    found = []
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") in ("Agent", "Task"):
                found.append(block.get("input", {}))
    return found


def verdict(case, calls):
    """Whether the run went as the case wants, and why not where it didn't."""
    fresh = [c for c in calls if c.get("subagent_type") != "fork"]
    if not calls:
        return False, "dispatched no agent"
    if len(fresh) < len(calls):
        return False, "forked the conversation"
    if case == "disagreement":
        settled = [c for c in fresh
                   if all(mark in c.get("prompt", "") for mark in (IMPLEMENTER_MARK, REVIEWER_MARK, BRIEF_MARK))]
        if not settled:
            return False, "no fresh agent got both positions and the brief"
    return True, f"{len(fresh)} fresh dispatch(es): " + ", ".join(c.get("subagent_type", "?") for c in fresh)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    models = sys.argv[2:] or ["sonnet", "opus"]
    misses = 0
    total = 0
    for model in models:
        for name, prompt in CASES:
            for run in range(runs):
                with tempfile.TemporaryDirectory() as repository:
                    Path(repository, "report.txt").write_text("report prints its summary\n")
                    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
                    start = time.time()
                    done = subprocess.run(
                        ["claude", "-p", prompt, "--model", model, "--plugin-dir", str(UNIT),
                         "--output-format", "stream-json", "--verbose", "--max-turns", "8",
                         "--disallowedTools", "Bash", "Edit", "Write"],
                        cwd=repository, capture_output=True, text=True, timeout=900)
                ok, why = verdict(name, dispatches(done.stdout))
                total += 1
                misses += not ok
                print(f"{model} {name} run {run + 1}: {'as wanted' if ok else 'missed'}, exit {done.returncode}, "
                      f"{time.time() - start:.0f}s, {why}", flush=True)
    print(f"\n{total - misses} of {total} runs as wanted, {misses} missed")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
