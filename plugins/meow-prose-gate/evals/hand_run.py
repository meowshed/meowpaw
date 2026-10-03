#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The hand run REQ-3752 asks for: each case, three times by default, through
the unit's own launcher with the real judge, printing the exit status, the
output and the wait. Every run calls a model, so no gate or workflow runs this:

    python3 plugins/meow-prose-gate/evals/hand_run.py 3
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

GATE = str(Path(__file__).resolve().parent.parent / "bin" / "meow-prose-gate")
PR = 'gh pr create --title "Bind the verbs to the crate" --body "{}"'
CASES = [
    ("bug1230-1", "pass", PR.format(
        "The verbs now run through the crate, so a repository without Python still gets them.\n\n"
        "Each verb resolves from the profile, and an undeclared one reports unresolved.\n\nCloses #12")),
    ("bug1230-2", "pass", PR.format(
        "I read the parser in depth and found two defects in how it reads a heredoc.\n\n"
        "Both are fixed here, each with a fixture seen failing first.")),
    ("bug1230-3", "pass", PR.format(
        "Look at the fixtures first: they hold the four cases the defect records.\n\n"
        "The gate passes on this tree, and `mise run all` exits 0.")),
    ("bug1230-4", "pass", PR.format(
        "This change replaces the prompt hook with a program.\n\n"
        "The program reads the command, takes the text from its arguments and checks three rules.\n\n"
        "Nothing else changes for a repository that installs the unit.")),
    ("j1-idiom", "block", PR.format(
        "This fix is a perfect storm of small changes, so we keep circling back to the cache.")),
    ("j2-acronym", "block", PR.format(
        "The TTL on each entry now comes from the profile, so a stale page expires on time.")),
    ("j3-bold-opener", "block", PR.format(
        "**Why.** The server rendered every page twice, so the cache now stores the result.")),
]
runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
env = {k: v for k, v in os.environ.items() if k != "MEOW_PROSE_GATE_JUDGE"}
for name, want, command in CASES:
    for run in range(runs):
        start = time.time()
        done = subprocess.run([GATE, "check"], input=json.dumps({"tool_input": {"command": command}}),
                              capture_output=True, text=True, env=env, timeout=200)
        got = "block" if done.returncode == 2 else "pass"
        out = (done.stderr + done.stdout).strip().replace("\n", " / ")
        print(f"{name} run {run + 1}: want {want}, exit {done.returncode} ({got}), "
              f"{time.time() - start:.1f}s, {out[:200]}", flush=True)
