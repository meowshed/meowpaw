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


def steps(lines, indent):
    """Each step at `indent` spaces, as the keys it declares."""
    found = []
    for line in lines:
        depth = len(line) - len(line.lstrip(" "))
        text = line.strip()
        if depth == indent and text.startswith("- "):
            found.append({})
            text = text[2:]
        elif depth != indent + 2 or not found:
            continue
        if re.match(r"[\w-]+:", text):
            key, value = text.split(":", 1)
            found[-1][key] = value.strip()
    return found


class TrunkGate(unittest.TestCase):
    def setUp(self):
        self.lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
        self.top = blocks(self.lines, 0)
        profile = tomllib.loads((ROOT / ".meowpaw" / "profile.toml").read_text(encoding="utf-8"))
        self.trunk = profile["git"]["trunk"]

    def assert_reaches_the_trunk(self, event, body, required):
        """A trigger whose filters leave the trunk out never runs the gate there."""
        inline = body[0].split(":", 1)[1].strip()
        self.assertEqual(inline, "", f"`{event}` carries its filters inline, in a form this test can't read")
        filters = blocks(body[1:], 4)
        for key in ("branches-ignore", "paths", "paths-ignore", "tags", "types"):
            self.assertNotIn(key, filters, f"`{event}` is filtered by `{key}`")
        if "branches" not in filters:
            self.assertFalse(required, f"`{event}` names no branch")
            return
        branches = re.search(r"branches:\s*\[([^\]]*)\]", "\n".join(filters["branches"]))
        self.assertIsNotNone(branches, f"`{event}` lists its branches in a form this test can't read")
        self.assertIn(self.trunk, [b.strip().strip("'\"") for b in branches.group(1).split(",")])

    def test_the_workflow_runs_on_a_pull_request_and_a_push_to_the_trunk(self):
        """TSK-4650 criterion 4, REQ-2210: the gate runs before a merge and again on the trunk."""
        triggers = blocks(self.top["on"][1:], 2)
        self.assertIn("pull_request", triggers)
        self.assertIn("push", triggers)
        self.assert_reaches_the_trunk("pull_request", triggers["pull_request"], required=False)
        self.assert_reaches_the_trunk("push", triggers["push"], required=True)

    def test_a_job_runs_the_whole_gate_unconditionally(self):
        """TSK-4650 criterion 4, REQ-2210: a job runs `mise run all`, and nothing skips it or forgives its failure."""
        jobs = blocks(self.top["jobs"][1:], 2)
        self.assertTrue(jobs, "the workflow declares no jobs")
        gates = []
        for name, body in jobs.items():
            keys = blocks(body[1:], 4)
            found = [s for s in steps(keys.get("steps", [])[1:], 6) if s.get("run") == "mise run all"]
            if not found:
                continue
            gates.append(name)
            for key in ("if", "continue-on-error", "needs"):
                self.assertNotIn(key, keys, f"job `{name}` declares `{key}`, so the gate may not run or count")
            for step in found:
                for key in ("if", "continue-on-error"):
                    self.assertNotIn(key, step, f"the gate step in `{name}` declares `{key}`")
        self.assertTrue(gates, f"no job runs `mise run all` among {sorted(jobs)}")


if __name__ == "__main__":
    unittest.main()
