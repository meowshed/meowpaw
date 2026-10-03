# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that every commit reaches the trunk through the gate, as TSK-4650
asks (REQ-2210, ADR-2530, SPC-1060).

The workflow is read as text, because the standard library has no YAML parser
and the check needs only the top-level trigger block and each job's steps.
"""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def blocks(lines, indent):
    """Each key at `indent` spaces, with the lines nested under it."""
    found, key = {}, None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        depth = len(line) - len(line.lstrip(" "))
        if depth == indent and re.match(r"[\w-]+:", line.strip()):
            key = line.strip().split(":", 1)[0]
            found[key] = [line]
        elif depth < indent:
            key = None
        elif key is not None:
            found[key].append(line)
    return found


class TrunkGate(unittest.TestCase):
    def setUp(self):
        self.lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
        self.top = blocks(self.lines, 0)
        profile = tomllib.loads((ROOT / ".meowpaw" / "profile.toml").read_text(encoding="utf-8"))
        self.trunk = profile["git"]["trunk"]

    def test_the_workflow_runs_on_a_pull_request_and_a_push_to_the_trunk(self):
        """TSK-4650 criterion 4, REQ-2210: the gate runs before a merge and again on the trunk."""
        triggers = blocks(self.top["on"][1:], 2)
        self.assertIn("pull_request", triggers)
        self.assertIn("push", triggers)
        push = "\n".join(triggers["push"])
        branches = re.search(r"branches:\s*\[([^\]]*)\]", push)
        self.assertIsNotNone(branches, push)
        self.assertIn(self.trunk, [b.strip().strip("'\"") for b in branches.group(1).split(",")])

    def test_a_job_runs_the_whole_gate_unconditionally(self):
        """TSK-4650 criterion 4, REQ-2210: a job runs `mise run all`, and no condition skips it."""
        jobs = blocks(self.top["jobs"][1:], 2)
        self.assertTrue(jobs, "the workflow declares no jobs")
        gates = [name for name, body in jobs.items()
                 if any(re.fullmatch(r"\s*(- )?run: mise run all\s*", line) for line in body)]
        self.assertTrue(gates, f"no job runs `mise run all` among {sorted(jobs)}")
        for name in gates:
            conditions = [line for line in blocks(jobs[name][1:], 4) if line == "if"]
            self.assertEqual(conditions, [], f"job `{name}` runs the gate only on a condition")


if __name__ == "__main__":
    unittest.main()
