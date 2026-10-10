# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The `test` stage runs each suite as a task it depends on, so they run at the same time (TSK-5280, REQ-4300)."""

import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def tasks():
    return tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))["tasks"]


def depends(task):
    value = task.get("depends", [])
    return [value] if isinstance(value, str) else list(value)


def reachable(all_tasks, start):
    """Every task `start` depends on, directly or through another."""
    seen, queue = [], depends(all_tasks[start])
    while queue:
        name = queue.pop(0)
        if name in seen or name not in all_tasks:
            continue
        seen.append(name)
        queue += depends(all_tasks[name])
    return seen


class TestStage(unittest.TestCase):
    def test_each_unit_suite_is_run_by_a_task_the_stage_depends_on(self):
        """TSK-5280 criterion 2, REQ-4300: a directory with tests under plugins/ is run by a task `test` depends on."""
        all_tasks = tasks()
        runs = {name: all_tasks[name].get("run", "") for name in reachable(all_tasks, "test")}
        missing = []
        for tests in sorted((ROOT / "plugins").glob("*/tests")):
            if not any(tests.glob("test_*.py")):
                continue
            where = f"plugins/{tests.parent.name}/tests"
            if not any(f"-s {where}" in run for run in runs.values()):
                missing.append(where)
        self.assertEqual(missing, [])

    def test_the_stage_itself_runs_no_suite(self):
        """TSK-5280 criterion 2, REQ-4300: the stage is the task that waits for the suites and runs none of its own."""
        self.assertEqual(tasks()["test"].get("run", ""), "")

    def test_the_gate_reads_a_stage_that_is_split_into_tasks(self):
        """TSK-5280 criterion 3, REQ-4300: `mise run test` is carried by `all` through the task name."""
        import check_gate_covers_verbs as gate
        split = {"test": {"depends": ["a", "b"]}, "a": {"run": "x"}, "b": {"run": "y"}}
        runs = {name: task.get("run", "") for name, task in split.items()}
        self.assertEqual(gate.covered("mise run test", ["test"], runs), (True, "the task test"))
        self.assertEqual(gate.covered("mise run test", ["a", "b"], runs), (False, "the task test"))

    def test_the_repository_gate_carries_the_stage(self):
        """TSK-5280 criterion 3, REQ-4300: this repository's `all` depends on `test`, and the check passes."""
        import check_gate_covers_verbs as gate
        all_tasks = tasks()
        self.assertIn("test", depends(all_tasks["all"]))
        self.assertTrue(reachable(all_tasks, "test"), "the test stage depends on nothing")
        self.assertEqual(gate.main(), 0)


if __name__ == "__main__":
    unittest.main()
