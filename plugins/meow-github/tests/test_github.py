# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for meow-github: the history read through a stand-in gh (ADR-1290)."""

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_GITHUB_BIN", UNIT / "bin" / "meow-github"))

ISSUE = {"number": 1, "title": "Refuse an empty title", "body": "It must refuse one.", "state": "open",
         "user": {"login": "ada"}, "html_url": "https://github.com/o/r/issues/1", "labels": [{"name": "bug"}]}
MERGED = dict(ISSUE, number=2, title="Refuse it", body="Closes #1", state="closed", pull_request={},
              html_url="https://github.com/o/r/pull/2", labels=[])
REJECTED = dict(MERGED, number=3, title="Warn instead", html_url="https://github.com/o/r/pull/3")
LISTINGS = {
    "repos/o/r/issues?state=all&per_page=100": [[ISSUE, MERGED], [REJECTED]],
    "repos/o/r/pulls?state=all&per_page=100": [[{"number": 2, "merged_at": "2026-01-01T00:00:00Z"},
                                               {"number": 3, "merged_at": None}]],
    "repos/o/r/issues/comments?per_page=100": [[{"issue_url": "https://api.github.com/repos/o/r/issues/3", "user": {"login": "bo"},
                                                "body": "A warning is ignored.", "html_url": "https://github.com/o/r/pull/3#c1"}]],
    "repos/o/r/pulls/comments?per_page=100": [[{"pull_request_url": "https://api.github.com/repos/o/r/pulls/2", "path": "a.txt",
                                               "user": {"login": "bo"}, "body": "Why here?", "html_url": "https://github.com/o/r/pull/2#r1"}]],
}
STAND_IN = """#!/bin/sh
printf '%s\\n' "$*" >> "$GH_LOG"
if [ "$1" = "api" ] && [ "$2" = "$GH_REFUSE" ]; then
  echo "HTTP 403: Resource not accessible by integration" >&2
  exit 1
fi
exec python3 -c 'import json, sys; print(json.dumps(json.load(open(sys.argv[1]))[sys.argv[2]]))' "$GH_DATA" "$2"
"""


class History(unittest.TestCase):
    def run_history(self, listings=LISTINGS, refuse=""):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "gh").write_text(STAND_IN, encoding="utf-8")
        (root / "gh").chmod(0o755)
        (root / "data.json").write_text(json.dumps(listings), encoding="utf-8")
        env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}", "GH_DATA": str(root / "data.json"),
               "GH_LOG": str(root / "log"), "GH_REFUSE": refuse}
        done = subprocess.run([str(BIN), "history", "o/r"], cwd=root, capture_output=True, text=True, env=env)
        calls = (root / "log").read_text(encoding="utf-8").splitlines() if (root / "log").exists() else []
        return done, calls

    def test_history_reads_every_listing_and_page(self):
        done, calls = self.run_history()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        history = json.loads(done.stdout)
        self.assertEqual([(i["number"], i["kind"], i["merged"]) for i in history["issues"]],
                         [(1, "issue", None), (2, "pull request", True), (3, "pull request", False)])
        self.assertEqual(history["issues"][0]["labels"], ["bug"])
        self.assertEqual(history["comments"], [{"on": 3, "author": "bo", "body": "A warning is ignored.", "url": "https://github.com/o/r/pull/3#c1"}])
        self.assertEqual(history["review_comments"][0]["on"], 2)
        self.assertEqual(len(calls), 4)
        for call in calls:
            self.assertTrue(call.endswith("--paginate --slurp --cache 1h"), call)

    def test_a_missing_field_fails_by_name(self):
        listings = dict(LISTINGS)
        listings["repos/o/r/issues?state=all&per_page=100"] = [[{k: v for k, v in ISSUE.items() if k != "title"}]]
        done, _ = self.run_history(listings)
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("lacks the field `title`", done.stdout)
        self.assertNotIn('"issues"', done.stdout)

    def test_a_refused_listing_leaves_the_history_unread(self):
        done, _ = self.run_history(refuse="repos/o/r/issues/comments?per_page=100")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("meow-github history: unread: conversation comments, repos/o/r/issues/comments?per_page=100: HTTP 403", done.stdout)
        self.assertIn("read before it stopped: issues and pull requests, pull requests;", done.stdout)
        self.assertNotIn('"issues"', done.stdout)


TRACKER = """#!/usr/bin/env python3
import json, os, sys
state_path = os.environ["GH_STATE"]
state = json.load(open(state_path)) if os.path.exists(state_path) else {"issues": {}, "calls": []}
args = sys.argv[1:]
state["calls"].append(args)
fields = {}
method = "GET"
i = 2
while i < len(args):
    if args[i] == "-X":
        method = args[i + 1]; i += 2
    elif args[i] == "-f":
        key, _, value = args[i + 1].partition("="); fields[key] = value; i += 2
    else:
        i += 1
path = args[1]
parts = path.split("/")
if method == "POST":
    number = len(state["issues"]) + 1
    state["issues"][str(number)] = {"number": number, "state": "open", **fields}
    out = state["issues"][str(number)]
elif method == "PATCH":
    state["issues"][parts[-1]].update(fields)
    out = state["issues"][parts[-1]]
else:
    out = state["issues"][parts[-1]]
json.dump(state, open(state_path, "w"))
print(json.dumps(out))
"""

EPIC = """---
id: EPC-0001
artifact: epic
status: {status}
revised: 2026-01-01
realises: ADR-0001
checked-at:
---

# A plan

## Tasks

- [ ] T-001 TSK-0001 the first
      closes: REQ-0001

- [ ] T-002 TSK-0002 the second
      closes: REQ-0002, REQ-0003
"""

TASK = """---
id: {id}
artifact: task
status: approved
revised: 2026-01-01
epic: EPC-0001
closes:
  [
{closes}
  ]
issue:
---

# {title}

Text.

## Depends on

{depends}

## Evidence

Not yet.
"""


class Project(unittest.TestCase):
    def repository(self, status="approved"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "project" / "epics").mkdir(parents=True)
        (root / "project" / "tasks").mkdir()
        (root / "project" / "epics" / "EPC-0001-a-plan.md").write_text(EPIC.format(status=status), encoding="utf-8")
        (root / "project" / "tasks" / "TSK-0001-first.md").write_text(TASK.format(
            id="TSK-0001", closes="    REQ-0001,", title="Refuse an empty title", depends="Nothing."), encoding="utf-8")
        (root / "project" / "tasks" / "TSK-0002-second.md").write_text(TASK.format(
            id="TSK-0002", closes="    REQ-0002,\n    REQ-0003,", title="Say why", depends="TSK-0001, whose check this reports."), encoding="utf-8")
        (root / "bin").mkdir()
        (root / "bin" / "gh").write_text(TRACKER, encoding="utf-8")
        (root / "bin" / "gh").chmod(0o755)
        return root

    def project(self, root, *extra):
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json")}
        return subprocess.run([str(BIN), "project", "EPC-0001", "o/r", *extra], cwd=root, capture_output=True, text=True, env=env)

    def state(self, root):
        return json.loads((root / "state.json").read_text(encoding="utf-8"))

    def task(self, root, name):
        return (root / "project" / "tasks" / name).read_text(encoding="utf-8")

    def test_an_approved_epic_projects_one_issue_per_task(self):
        root = self.repository()
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        issues = self.state(root)["issues"]
        self.assertEqual(sorted(i["title"] for i in issues.values()), ["TSK-0001: Refuse an empty title", "TSK-0002: Say why"])
        second = issues["2"]["body"]
        self.assertIn("TSK-0002 of EPC-0001, which realises ADR-0001.", second)
        self.assertIn("Closes REQ-0002, REQ-0003.", second)
        self.assertIn("Depends on: TSK-0001, whose check this reports.", second)
        self.assertRegex(second, r"<!-- meow-github: projected from TSK-0002 at [0-9a-f]{12} -->$")
        text = self.task(root, "TSK-0002-second.md")
        self.assertIn("\nissue: 2\n", text)
        self.assertRegex(text, r"\nprojected: [0-9a-f]{12}\n---\n")
        self.assertIn("TSK-0001: projected to issue #1 at", done.stdout)
        self.assertIn("read back", done.stdout)
        gets = [c for c in self.state(root)["calls"] if "-X" not in c]
        self.assertEqual([c[1] for c in gets], ["repos/o/r/issues/1", "repos/o/r/issues/2"])

    def test_the_fingerprint_is_reproducible_by_hand(self):
        root = self.repository()
        self.project(root)
        issue = self.state(root)["issues"]["1"]
        body = issue["body"].rsplit("\n\n", 1)[0]
        by_hand = hashlib.sha256(f"{issue['title']}\n{body}".encode()).hexdigest()[:12]
        self.assertIn(f"\nprojected: {by_hand}\n", self.task(root, "TSK-0001-first.md"))

    def test_a_replay_changes_nothing(self):
        root = self.repository()
        self.project(root)
        before = (self.state(root), self.task(root, "TSK-0001-first.md"))
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(len(self.state(root)["issues"]), 2)
        self.assertFalse([c for c in self.state(root)["calls"][len(before[0]["calls"]):] if "-X" in c])
        self.assertEqual(before[1], self.task(root, "TSK-0001-first.md"))
        self.assertIn("TSK-0001: unchanged, issue #1 at", done.stdout)

    def writes(self, root, since=0):
        return [c for c in self.state(root)["calls"][since:] if "-X" in c]

    def test_a_changed_task_updates_its_issue(self):
        root = self.repository()
        self.project(root)
        before = self.task(root, "TSK-0001-first.md")
        (root / "project" / "tasks" / "TSK-0001-first.md").write_text(before.replace("# Refuse an empty title", "# Refuse a blank title"), encoding="utf-8")
        calls = len(self.state(root)["calls"])
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(self.state(root)["issues"]["1"]["title"], "TSK-0001: Refuse a blank title")
        self.assertEqual([c[:4] for c in self.writes(root, calls)], [["api", "repos/o/r/issues/1", "-X", "PATCH"]])
        self.assertNotEqual(before.split("projected: ")[1][:12], self.task(root, "TSK-0001-first.md").split("projected: ")[1][:12])

    def test_an_issue_edited_on_github_is_reported_and_left(self):
        root = self.repository()
        self.project(root)
        state = self.state(root)
        state["issues"]["1"]["body"] = "Rewritten by a person."
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        done = self.project(root)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0001: issue #1 was edited on GitHub since it was projected", done.stdout)
        self.assertEqual(self.state(root)["issues"]["1"]["body"], "Rewritten by a person.")
        self.assertFalse(self.writes(root, len(state["calls"])))

    def test_a_closed_issue_on_an_unmarked_task_is_reported_and_check_writes_nothing(self):
        root = self.repository()
        self.project(root)
        state = self.state(root)
        state["issues"]["2"]["state"] = "closed"
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        tasks = [self.task(root, n) for n in ("TSK-0001-first.md", "TSK-0002-second.md")]
        (root / "project" / "tasks" / "TSK-0001-first.md").write_text(tasks[0].replace("# Refuse an empty title", "# Refuse a blank title"), encoding="utf-8")
        done = self.project(root, "--check")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0002: issue #2 is closed on GitHub while EPC-0001 leaves the task unmarked", done.stdout)
        self.assertIn("TSK-0001: changed since it was projected at", done.stdout)
        self.assertIn("would be updated", done.stdout)
        self.assertFalse(self.writes(root, len(state["calls"])))
        self.assertEqual(self.state(root)["issues"]["1"]["title"], "TSK-0001: Refuse an empty title")
        self.assertEqual(self.task(root, "TSK-0002-second.md"), tasks[1])

    def test_a_draft_epic_projects_nothing(self):
        root = self.repository(status="draft")
        done = self.project(root)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("EPC-0001 is draft, and its tasks are projected only once it is approved", done.stdout)
        self.assertFalse((root / "state.json").exists())


class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-github"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-github").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "history"], cwd=tmp, capture_output=True, text=True)
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
            self.assertIn("unread", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("reinstall the unit", done.stdout)


if __name__ == "__main__":
    unittest.main()
