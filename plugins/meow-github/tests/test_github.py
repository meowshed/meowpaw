# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for meow-github: the history read and the projection through a stand-in gh (ADR-1290, ADR-1810)."""

import calendar
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
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
# ADR-1810: under `--include` the stand-in prints a status line and a header block before the body, with a `Link`
# header naming the next page, and a refused call's block too, as RES-0290 saw gh 2.101.0 do.
STAND_IN = """#!/usr/bin/env python3
import email.utils, json, os, sys
args = sys.argv[1:]
open(os.environ["GH_LOG"], "a").write(" ".join(args) + "\\n")
path = args[1].removeprefix("https://api.github.com/")
base, _, page = path.partition("&page=")
page = int(page or 1)
link = None
if path == os.environ["GH_REFUSE"]:
    status, body = 403, {"message": "Resource not accessible by integration"}
else:
    pages = json.load(open(os.environ["GH_DATA"]))[base]
    status, body = 200, pages[page - 1]
    if page < len(pages):
        link = f'<https://api.github.com/{base}&page={page + 1}>; rel="next"'
if "--include" in args:
    print(f"HTTP/2.0 {status} {'OK' if status == 200 else 'Forbidden'}")
    print("Date: " + email.utils.formatdate(usegmt=True))
    if link:
        print("Link: " + link)
    print()
print(json.dumps(body))
if status >= 400:
    print(f"gh: {body['message']} (HTTP {status})", file=sys.stderr)
    sys.exit(1)
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
        # ADR-1810: one page a call, following `Link`, and every read but the run's first through the cache.
        self.assertEqual(len(calls), 5, calls)
        self.assertIn("repos/o/r/issues?state=all&per_page=100&page=2", calls[1])
        self.assertTrue(calls[0].endswith(" --include"), calls[0])
        for call in calls[1:]:
            self.assertTrue(call.endswith(" --include --cache 1h"), call)

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

    def test_the_document_names_the_credential_and_the_budget(self):
        """TSK-2950 criterion 6, REQ-2568, REQ-2582: the document carries `credential`, the form, and `budget`, the
        budget lines naming the four counts, and every field onboarding reads is as it was."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        # The layered stand-in and its runner, defined below with the request layer's checks.
        Layered.stand_in(self, root, {"listings": SINGLE_PAGES})
        done = Layered.meow_github(self, root, "history", "o/r", credential={})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        document = json.loads(done.stdout)
        self.assertEqual(document.get("credential"), FORMS[None], document.keys())
        budget = document.get("budget")
        self.assertIsInstance(budget, list, budget)
        self.assertTrue(all(isinstance(line, str) for line in budget), budget)
        for count in COUNTS:
            self.assertEqual(len([line for line in budget if count in line]), 1, (count, budget))
        read = {k: v for k, v in document.items() if k not in ("credential", "budget")}
        issue = {"number": 1, "kind": "issue", "title": ISSUE["title"], "body": ISSUE["body"], "state": "open",
                 "merged": None, "author": "ada", "url": ISSUE["html_url"], "labels": ["bug"]}
        pull = {"number": 2, "kind": "pull request", "title": MERGED["title"], "body": MERGED["body"],
                "state": "closed", "merged": True, "author": "ada", "url": MERGED["html_url"], "labels": []}
        self.assertEqual(read, {"repository": "o/r", "issues": [issue, pull], "comments": [], "review_comments": []})


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
elif parts[-1].startswith("issues?"):
    out = list(state["issues"].values())
else:
    out = state["issues"][parts[-1]]
json.dump(state, open(state_path, "w"))
if "--include" in args:
    import email.utils
    print(f"HTTP/2.0 {201 if method == 'POST' else 200} OK")
    print("Date: " + email.utils.formatdate(usegmt=True))
    print()
print(json.dumps(out))
"""

# The read-back listing `project` sends after its last create (SPC-1080), with `since` as a UTC time.
LISTING = r"^repos/o/r/issues\?state=all&since=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)&per_page=100$"

EPIC = """---
id: EPC-0001
artifact: epic
status: {status}
revised: 2026-01-01
realises: ADR-0001
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
    def repository(self, status="approved", tracker='[tracker]\nkind = "github"\n'):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / ".meowpaw").mkdir()
        (root / ".meowpaw" / "profile.toml").write_text(tracker, encoding="utf-8")
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
        self.assertEqual(len(gets), 1, gets)
        self.assertRegex(gets[0][1], LISTING)

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

    def test_a_task_with_no_issue_field_gets_one_and_a_replay_opens_nothing(self):
        """REQ-1382, REQ-1386: the mapping is written on the task even where the field was missing, so a replay is no action."""
        root = self.repository()
        path = root / "project" / "tasks" / "TSK-0001-first.md"
        path.write_text(path.read_text(encoding="utf-8").replace("issue:\n", "", 1), encoding="utf-8")
        self.project(root)
        self.assertRegex(self.task(root, "TSK-0001-first.md"), r"\nissue: 1\nprojected: [0-9a-f]{12}\n---\n")
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(len(self.state(root)["issues"]), 2)
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

    def test_a_repository_declaring_no_tracker_projects_nothing(self):
        root = self.repository(tracker="[verbs]\n")
        done = self.project(root)
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn(".meowpaw/profile.toml declares no tracker, so nothing is projected; declare `[tracker] kind = \"github\"`", done.stdout)
        self.assertFalse((root / "state.json").exists())
        self.assertNotIn("issue: 1", self.task(root, "TSK-0001-first.md"))

    def test_project_groups_an_issue_nowhere(self):
        """TSK-2910 criterion 4, REQ-3320: `project` passes no grouping argument and no grouping field, so an issue
        sits under nothing on the tracker, and the body copies a dependency line's `(not blocking)` as written."""
        root = self.repository()
        path = root / "project" / "tasks" / "TSK-0002-second.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "TSK-0001, whose check this reports.", "- TSK-0001 (not blocking): shares a helper"), encoding="utf-8")
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = self.state(root)["calls"]
        self.assertTrue(self.writes(root), calls)
        # ADR-1810: every call ends with the request layer's `--include`, which groups nothing; the shape is read
        # without it.
        for call in calls:
            self.assertEqual(call[-1], "--include", call)
        calls = [call[:-1] for call in calls]
        for call in calls:
            for flag in ("--milestone", "--parent", "--project", "--label"):
                self.assertFalse([a for a in call if a == flag or a.startswith(flag + "=")], call)
            fields = [call[i + 1].partition("=")[0] for i, a in enumerate(call[:-1]) if a in ("-f", "-F", "--field", "--raw-field")]
            self.assertLessEqual(set(fields), {"title", "body"}, call)
            # BUG-1301: each call has exactly one of the three shapes `project` sends, so a grouping sent through
            # `--input`, an `--add-` flag or an extra argument of any other kind fails here.
            self.assertEqual(call[0], "api", call)
            self.assertRegex(call[1], r"^repos/o/r/issues(/\d+|\?state=all&since=[^&]+&per_page=100)?$", call)
            if len(call) > 2:
                self.assertEqual(len(call), 8, call)
                self.assertIn(call[2:4], (["-X", "POST"], ["-X", "PATCH"]), call)
                self.assertEqual([call[4], call[6]], ["-f", "-f"], call)
                self.assertTrue(call[5].startswith("title=") and call[7].startswith("body="), call)
        self.assertIn("- TSK-0001 (not blocking): shares a helper", self.state(root)["issues"]["2"]["body"])

    def test_a_task_realising_a_decision_projects_with_no_parent(self):
        """TSK-3810 criterion 4, REQ-3630: a task naming `realises` and no epic projects as one issue under nothing."""
        root = self.repository()
        (root / "project" / "adrs").mkdir()
        (root / "project" / "adrs" / "ADR-0002-a-choice.md").write_text(
            "---\nid: ADR-0002\nartifact: adr\nstatus: approved\nrevised: 2026-01-01\naddresses: [REQ-0004]\n---\n\n# 0002. A choice\n",
            encoding="utf-8")
        (root / "project" / "tasks" / "TSK-0003-direct.md").write_text(TASK.format(
            id="TSK-0003", closes="    REQ-0004,", title="Do it directly", depends="Nothing.").replace(
            "epic: EPC-0001", "realises: ADR-0002"), encoding="utf-8")
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json")}
        done = subprocess.run([str(BIN), "project", "ADR-0002", "o/r"], cwd=root, capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        issues = self.state(root)["issues"]
        self.assertEqual([i["title"] for i in issues.values()], ["TSK-0003: Do it directly"])
        self.assertIn("TSK-0003, which realises ADR-0002.", issues["1"]["body"])
        self.assertIn("\nissue: 1\n", self.task(root, "TSK-0003-direct.md"))

    def direct(self, root, adr_status="approved"):
        (root / "project" / "adrs").mkdir(exist_ok=True)
        (root / "project" / "adrs" / "ADR-0002-a-choice.md").write_text(
            f"---\nid: ADR-0002\nartifact: adr\nstatus: {adr_status}\nrevised: 2026-01-01\naddresses: [REQ-0004]\n---\n\n# 0002. A choice\n",
            encoding="utf-8")
        (root / "project" / "tasks" / "TSK-0003-direct.md").write_text(TASK.format(
            id="TSK-0003", closes="    REQ-0004,", title="Do it directly", depends="Nothing.").replace(
            "epic: EPC-0001", "realises: ADR-0002"), encoding="utf-8")

    def run_on(self, root, target):
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json")}
        return subprocess.run([str(BIN), "project", target, "o/r"], cwd=root, capture_output=True, text=True, env=env)

    def test_a_draft_decision_projects_nothing(self):
        """REQ-3630: a draft decision's direct tasks wait for its approval, as an epic's do."""
        root = self.repository()
        self.direct(root, adr_status="draft")
        done = self.run_on(root, "ADR-0002")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0002 is draft", done.stdout)

    def test_a_task_under_an_epic_is_not_projected_under_its_decision(self):
        """REQ-3630: a task naming an epic belongs to the epic, even where it also names the decision."""
        root = self.repository()
        self.direct(root)
        path = root / "project" / "tasks" / "TSK-0003-direct.md"
        path.write_text(path.read_text(encoding="utf-8").replace("realises: ADR-0002", "epic: EPC-0001\nrealises: ADR-0002"), encoding="utf-8")
        done = self.run_on(root, "ADR-0002")
        self.assertIn("ADR-0002 has no tasks", done.stdout)

    def test_a_draft_epic_projects_nothing(self):
        root = self.repository(status="draft")
        done = self.project(root)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("EPC-0001 is draft, and its tasks are projected only once it is approved", done.stdout)
        self.assertFalse((root / "state.json").exists())


# ADR-1810: the stand-in `gh` the request layer's checks run against. It prints a status line and a header block
# before the body under `--include`, as RES-0290 saw gh 2.101.0 do, and prints a refused call's block too. Its `Date`
# is the injected local clock, the file MEOW_GITHUB_CLOCK names, less GH_SKEW seconds. The run under test reads the
# same file as its clock and sleeps by adding the seconds to it, so no check waits in real time. GH_SCRIPT names a
# JSON file: `responses` holds, for each "<METHOD> <path>", the answers to give in turn before the default one,
# `listings` holds each listing's body, `bare` leaves every rate-limit header out, `headers` replaces rate-limit
# headers on every response, and `cached` gives the age, `remaining` and reset of the headers a call sent with
# `--cache` replays. A `null` among the `responses` lets that call through to the default answer. Each issue holds
# the time on GitHub's clock it was written at, and the read-back listing answers with the issues written at or after
# its `since`, less the numbers `omit` names.
LAYERED = """#!/usr/bin/env python3
import calendar, email.utils, json, os, sys, time
state_path = os.environ["GH_STATE"]
state = json.load(open(state_path)) if os.path.exists(state_path) else {"issues": {}, "calls": [], "used": {}}
script = json.load(open(os.environ["GH_SCRIPT"]))
now = float(open(os.environ["MEOW_GITHUB_CLOCK"]).read())
github_now = now - float(os.environ.get("GH_SKEW", "0"))
args = sys.argv[1:]
state["calls"].append({"args": args, "at": now})
method, fields, path, i = "GET", {}, None, 1
while i < len(args):
    a = args[i]
    if a in ("-X", "--method"):
        method = args[i + 1]; i += 2
    elif a.startswith("--method="):
        method = a.split("=", 1)[1]; i += 1
    elif a in ("-f", "-F", "--field", "--raw-field"):
        key, _, value = args[i + 1].partition("="); fields[key] = value; i += 2
    elif a in ("--cache", "-H", "--header", "-q", "--jq", "--input", "-t", "--template"):
        i += 2
    elif a.startswith("-"):
        i += 1
    else:
        path = path or a.removeprefix("https://api.github.com/"); i += 1
key = f"{method} {path}"
headers = {"Date": email.utils.formatdate(github_now, usegmt=True)}
if not script.get("bare"):
    headers.update({"X-Ratelimit-Limit": "5000", "X-Ratelimit-Remaining": "4990", "X-Ratelimit-Used": "10",
                    "X-Ratelimit-Resource": "core", "X-Ratelimit-Reset": str(int(github_now) + 3600)})
    headers.update(script.get("headers", {}))
cached = script.get("cached")
if cached and "--cache" in args:
    stored = github_now - cached["age"]
    headers.update({"Date": email.utils.formatdate(stored, usegmt=True),
                    "X-Ratelimit-Remaining": str(cached["remaining"]),
                    "X-Ratelimit-Reset": str(int(github_now) + cached["reset_in"])})
queue = script.get("responses", {}).get(key, [])
used = state["used"].get(key, 0)
answer = None
if used < len(queue):
    state["used"][key] = used + 1
    answer = queue[used]
if answer is not None:
    status, body = answer["status"], answer.get("body", {"message": "scripted"})
    headers.update(answer.get("headers", {}))
elif method == "POST":
    number = len(state["issues"]) + 1
    state["issues"][str(number)] = {"number": number, "state": "open", "written": github_now, **fields}
    status, body = 201, state["issues"][str(number)]
elif method == "PATCH":
    state["issues"][path.split("/")[-1]].update(fields, written=github_now)
    status, body = 200, state["issues"][path.split("/")[-1]]
elif path.startswith("repos/o/r/issues?state=all&since="):
    since = calendar.timegm(time.strptime(path.split("since=")[1].split("&")[0], "%Y-%m-%dT%H:%M:%SZ"))
    status, body = 200, [issue for issue in state["issues"].values()
                         if issue["written"] >= since and issue["number"] not in script.get("omit", [])]
elif path in script.get("listings", {}):
    status, body = 200, script["listings"][path]
elif path.split("/")[-1] in state["issues"]:
    status, body = 200, state["issues"][path.split("/")[-1]]
else:
    status, body = 404, {"message": "Not Found"}
json.dump(state, open(state_path, "w"))
if "--include" in args:
    reason = {200: "OK", 201: "Created", 403: "Forbidden", 404: "Not Found", 429: "Too Many Requests"}.get(status, "")
    print(f"HTTP/2.0 {status} {reason}")
    for name, value in headers.items():
        print(f"{name}: {value}")
    print()
print(json.dumps([body] if "--slurp" in args else body))
if status >= 400:
    print(f"gh: {body.get('message', '')} (HTTP {status})", file=sys.stderr)
    sys.exit(1)
"""

# The local clock every layered check starts at: the moment RES-0290 read `date -u +%s`, 14:30:37 UTC on 2026-09-29.
START = 1790692237
SECONDARY = {"message": "You have exceeded a secondary rate limit. Please wait a few minutes before you try again."}


class Layered:
    """Runs `meow-github` against the stand-in above, with an injected clock and sleep."""

    def stand_in(self, root, script):
        (root / "bin").mkdir(exist_ok=True)
        (root / "bin" / "gh").write_text(LAYERED, encoding="utf-8")
        (root / "bin" / "gh").chmod(0o755)
        (root / "script.json").write_text(json.dumps(script), encoding="utf-8")
        (root / "clock").write_text(str(START), encoding="utf-8")

    def meow_github(self, root, *args, skew=0, credential=None):
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json"),
               "GH_SCRIPT": str(root / "script.json"), "MEOW_GITHUB_CLOCK": str(root / "clock"), "GH_SKEW": str(skew)}
        if credential is not None:
            # The variables that name the credential's form are set only as the check states, whatever the shell
            # running the checks, CI's included, carries.
            env = {k: v for k, v in env.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_ACTIONS")}
            env.update(credential)
        return subprocess.run([str(BIN), *args], cwd=root, capture_output=True, text=True, env=env)

    def calls(self, root):
        path = root / "state.json"
        return json.loads(path.read_text(encoding="utf-8"))["calls"] if path.exists() else []

    def clock(self, root):
        return float((root / "clock").read_text(encoding="utf-8"))

    def throttled_line(self, done):
        lines = [line for line in done.stdout.splitlines() if "throttled" in line]
        self.assertTrue(lines, done.stdout + done.stderr)
        return lines[0]

    def retry_after(self, line):
        """The UTC time and the header a `throttled` line names, as `retry after <UTC time> (<header>)` states."""
        found = re.search(r"retry after (.+?) \(([^)]+)\)", line)
        self.assertTrue(found, line)
        for form in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S UTC", "%Y-%m-%dT%H:%M:%S+00:00", "%a, %d %b %Y %H:%M:%S GMT"):
            try:
                return calendar.timegm(time.strptime(found.group(1), form)), found.group(2).lower()
            except ValueError:
                continue
        self.fail(f"no UTC time in {line!r}")


def create(call):
    return call["args"][:2] == ["api", "repos/o/r/issues"] and "POST" in call["args"]


class Throttle(Layered, unittest.TestCase):
    """ADR-1810: a throttled `project` stops at the stated wait, or sleeps it under `--wait`, never past an hour."""

    def throttled_project(self, *answers):
        root = Project.repository(self)
        self.stand_in(root, {"responses": {"POST repos/o/r/issues": list(answers)}})
        return root

    def test_a_stated_wait_stops_the_run(self):
        """TSK-2940 criterion 1, REQ-2566: a 403 with `retry-after: 30` prints `throttled`, the method, the endpoint
        and the UTC time 30 seconds after the response, exits 3 and sends no further call."""
        root = self.throttled_project({"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY})
        done = self.meow_github(root, "project", "EPC-0001", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        line = self.throttled_line(done)
        self.assertIn("POST repos/o/r/issues", line)
        self.assertEqual(self.retry_after(line), (START + 30, "retry-after"))
        calls = self.calls(root)
        self.assertEqual(len([c for c in calls if create(c)]), 1, calls)
        self.assertTrue(create(calls[-1]), calls)

    def test_wait_resends_no_earlier_than_the_stated_time(self):
        """TSK-2940 criterion 2, REQ-2566: under `--wait` the refused call is sent again no earlier than the
        `retry-after` time, on the injected clock."""
        root = self.throttled_project({"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY})
        done = self.meow_github(root, "project", "EPC-0001", "o/r", "--wait")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        creates = [c for c in self.calls(root) if create(c)]
        self.assertGreaterEqual(len(creates), 2, creates)
        self.assertGreaterEqual(creates[1]["at"], creates[0]["at"] + 30, creates)

    def test_wait_stops_once_the_waits_would_pass_an_hour(self):
        """TSK-2940 criterion 3, REQ-2566: under `--wait`, 3,540 seconds are slept, and a second throttle of 120
        seconds, which would take the waits past an hour, starts no sleep and stops the run as throttled."""
        root = self.throttled_project({"status": 403, "headers": {"Retry-After": "3540"}, "body": SECONDARY},
                                      {"status": 403, "headers": {"Retry-After": "120"}, "body": SECONDARY})
        done = self.meow_github(root, "project", "EPC-0001", "o/r", "--wait")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.throttled_line(done)
        creates = [c for c in self.calls(root) if create(c)]
        self.assertEqual(len(creates), 2, creates)
        self.assertGreaterEqual(creates[1]["at"], START + 3540, creates)
        self.assertTrue(create(self.calls(root)[-1]), self.calls(root))
        self.assertGreaterEqual(self.clock(root), START + 3540)
        self.assertLess(self.clock(root), START + 3540 + 120, "a second sleep was started")

    def test_an_unparsed_wait_is_unknown_and_stops_the_run(self):
        """TSK-2940 criterion 5, REQ-2578: a `retry-after` that isn't a number of seconds gives an unknown wait, and
        the run sends no further call and exits 3, under `--wait` as without it, sleeping nothing."""
        for extra in ((), ("--wait",)):
            with self.subTest(extra=extra):
                root = self.throttled_project(
                    {"status": 403, "headers": {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}, "body": SECONDARY})
                done = self.meow_github(root, "project", "EPC-0001", "o/r", *extra)
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                line = self.throttled_line(done)
                self.assertIn("POST repos/o/r/issues", line)
                self.assertIn("unknown", line)
                calls = self.calls(root)
                self.assertEqual(len([c for c in calls if create(c)]), 1, calls)
                self.assertTrue(create(calls[-1]), calls)
                self.assertEqual(self.clock(root), START)


SINGLE_PAGES = {
    "repos/o/r/issues?state=all&per_page=100": [ISSUE, MERGED],
    "repos/o/r/pulls?state=all&per_page=100": [{"number": 2, "merged_at": "2026-01-01T00:00:00Z"}],
    "repos/o/r/issues/comments?per_page=100": [],
    "repos/o/r/pulls/comments?per_page=100": [],
}


class Limits(Layered, unittest.TestCase):
    """ADR-1810: the layer reads every response's limit headers, and never reads a replay's as current."""

    def history(self, script, skew=0):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.stand_in(root, {"listings": SINGLE_PAGES, **script})
        return root, self.meow_github(root, "history", "o/r", skew=skew)

    def test_a_response_with_no_limit_header_lets_the_run_go_on(self):
        """TSK-2940 criterion 6, REQ-2566: responses carrying no rate-limit header, read through `--include`, are
        taken as carrying none, not as a limit reached, and the run reads every listing."""
        root, done = self.history({"bare": True})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("throttled", done.stdout)
        self.assertEqual([i["number"] for i in json.loads(done.stdout)["issues"]], [1, 2])
        calls = self.calls(root)
        self.assertEqual(len(calls), 4, calls)
        for call in calls:
            self.assertIn("--include", call["args"], call)

    def test_a_stale_replay_is_not_read_as_current(self):
        """TSK-2940 criterion 7, REQ-2566: a cached response whose `Date` is ten minutes old carries
        `x-ratelimit-remaining: 0`; read as current it would hold the next read, so the run reading every listing
        shows its `remaining` wasn't taken as current."""
        root, done = self.history({"cached": {"age": 600, "remaining": 0, "reset_in": 1800}})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("throttled", done.stdout)
        self.assertEqual(json.loads(done.stdout)["repository"], "o/r")
        calls = self.calls(root)
        self.assertEqual(len(calls), 4, calls)
        self.assertNotIn("--cache", calls[0]["args"], calls[0])
        for call in calls:
            self.assertIn("--include", call["args"], call)
        for call in calls[1:]:
            self.assertIn("--cache", call["args"], call)

    def test_a_skewed_clock_leaves_a_fresh_response_current(self):
        """TSK-2940 criterion 7, REQ-2566: with the local clock two minutes ahead of the stand-in's `Date`, a fresh
        cached response is current, so its `remaining: 0` holds the next read to the same resource and the run
        stops as throttled at the reset; the run's first call carries no `--cache`."""
        root, done = self.history({"cached": {"age": 0, "remaining": 0, "reset_in": 1800}}, skew=120)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        line = self.throttled_line(done)
        self.assertIn("GET repos/o/r/issues/comments?per_page=100", line)
        self.assertEqual(self.retry_after(line), (START - 120 + 1800, "x-ratelimit-reset"))
        calls = self.calls(root)
        self.assertEqual(len(calls), 2, calls)
        self.assertNotIn("--cache", calls[0]["args"], calls[0])
        self.assertIn("--cache", calls[1]["args"], calls[1])


# ADR-1810, SPC-1080 "The GitHub request layer": the four counts the layer keeps, named on a report's last lines.
COUNTS = ("primary requests", "secondary points", "content creation", "spacing")
FORMS = {"GH_TOKEN": "GH_TOKEN from the environment", "GITHUB_TOKEN": "GITHUB_TOKEN from the environment",
         None: "gh's stored credential"}
ACTIONS = ", inside a GitHub Actions workflow"
# A token value no check's output may carry. It is shaped like no real token, so a kept run carrying it by mistake
# trips no secret scan.
SENTINEL = "meow-sentinel-6d1f0b7e"


def many_tasks(test, count):
    """A repository whose approved epic lists `count` unmapped tasks."""
    root = Project.repository(test)
    tasks = root / "project" / "tasks"
    for old in tasks.iterdir():
        old.unlink()
    lines = []
    for n in range(1, count + 1):
        task = f"TSK-{n:04d}"
        lines.append(f"- [ ] T-{n:03d} {task} task {n}\n      closes: REQ-0001\n")
        (tasks / f"{task}-task-{n}.md").write_text(TASK.format(
            id=task, closes="    REQ-0001,", title=f"Task {n}", depends="Nothing."), encoding="utf-8")
    epic = EPIC.format(status="approved").split("## Tasks")[0] + "## Tasks\n\n" + "\n".join(lines)
    (root / "project" / "epics" / "EPC-0001-a-plan.md").write_text(epic, encoding="utf-8")
    return root


class Budgets(Layered, unittest.TestCase):
    """ADR-1810: the layer keeps the four counts, spaces the writes, and stops before a request past a ceiling."""

    run_of_501 = None

    def five_hundred_and_one(self):
        """One `project` run over 501 unmapped tasks, shared by the checks that read it: its result and the calls
        the stand-in recorded, read before the first check's repository is removed."""
        if Budgets.run_of_501 is None:
            root = many_tasks(self, 501)
            self.stand_in(root, {})
            done = self.meow_github(root, "project", "EPC-0001", "o/r", credential={})
            Budgets.run_of_501 = (done, self.calls(root))
        return Budgets.run_of_501

    def test_content_creation_stops_the_run_at_500_an_hour(self):
        """TSK-2950 criterion 1, REQ-2568: with 501 unmapped tasks the stand-in records 500 creates, and the run
        stops before the 501st, naming content creation at 500 of 500 this hour, and exits 3."""
        done, calls = self.five_hundred_and_one()
        self.assertEqual(done.returncode, 3, done.stdout[-2000:] + done.stderr)
        self.assertEqual(len([c for c in calls if create(c)]), 500, done.stdout[-2000:])
        self.assertIn("(content creation: 500 of 500 this hour)", self.throttled_line(done))

    def test_writes_are_a_second_apart(self):
        """TSK-2950 criterion 2, REQ-2568: in the same run, every write the stand-in records is at least one second
        after the previous one, on the injected clock."""
        done, calls = self.five_hundred_and_one()
        writes = [c for c in calls if "-X" in c["args"] or any(a.startswith("--method") for a in c["args"])]
        self.assertGreater(len(writes), 1, done.stdout[-2000:])
        close = [(a["at"], b["at"]) for a, b in zip(writes, writes[1:]) if b["at"] - a["at"] < 1]
        self.assertEqual(len(close), 0, f"writes less than a second after the previous one, the first {close[:1]}")

    def test_the_budget_lines_name_the_four_counts(self):
        """TSK-2950 criterion 3, REQ-2568: with `x-ratelimit-limit: 1000` and `GITHUB_ACTIONS=true`, the last lines
        of `project`'s report name primary requests with 1,000 as the limit, read from the header and never assumed
        from the credential's form, then secondary points, content creation and spacing."""
        # 1234 is a limit no credential's form implies, so a limit assumed from the form can't pass for one read.
        for limit, shown in (("1000", "1,000"), ("1234", "1,234")):
            with self.subTest(limit=limit):
                root = Project.repository(self)
                self.stand_in(root, {"headers": {"X-Ratelimit-Limit": limit}})
                done = self.meow_github(root, "project", "EPC-0001", "o/r", credential={"GITHUB_ACTIONS": "true"})
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                tail = done.stdout.splitlines()[-len(COUNTS):]
                self.assertEqual([line.split(":")[0] for line in tail], list(COUNTS), tail)
                creates = len([c for c in self.calls(root) if create(c)])
                reads = len(self.calls(root)) - creates
                self.assertGreater(creates, 0)
                self.assertGreater(reads, 0)
                self.assertTrue(tail[0].startswith(
                    f"primary requests: {creates + reads} sent; core limit {shown}, 4,990 remaining, resets "), tail)
                self.assertEqual(tail[1:], [
                    f"secondary points: {reads + 5 * creates} of 900 this minute",
                    f"content creation: {creates} of 80 this minute, {creates} of 500 this hour",
                    f"spacing: {creates} writes, each at least one second after the previous one"])


def groups(test, done):
    """The three groups of the one `partial:` line a report holds, each as the text after its name."""
    lines = [line for line in done.stdout.splitlines() if line.startswith("partial: ")]
    test.assertEqual(len(lines), 1, done.stdout + done.stderr)
    found = re.fullmatch(r"partial: projected (.+); created, not read back (.+); not projected (.+)", lines[0])
    test.assertTrue(found, lines[0])
    return found.groups()


def listings(calls):
    """The read-back listings among the recorded calls, each as the `since` it carries."""
    sent = [re.match(LISTING, call["args"][1]) for call in calls if call["args"][0] == "api"]
    return [found.group(1) for found in sent if found]


class Partial(Layered, unittest.TestCase):
    """ADR-1810: created issues are read back in one listing, and a run that stops part way says what it did."""

    REFUSED = {"status": 422, "body": {"message": "Validation Failed"}}

    def five(self, script, skew=0):
        root = many_tasks(self, 5)
        self.stand_in(root, script)
        return root, self.meow_github(root, "project", "EPC-0001", "o/r", skew=skew)

    def test_a_failed_write_reads_back_and_reports_partial(self):
        """TSK-2960 criterion 1, REQ-2572: with the third of five creates failing, `project` sends the read-back
        listing, names the first two tasks as projected and the other three as not projected, and exits 3."""
        root, done = self.five({"responses": {"POST repos/o/r/issues": [None, None, self.REFUSED]}})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        calls = self.calls(root)
        self.assertEqual(len([c for c in calls if create(c)]), 3, calls)
        self.assertEqual(len(listings(calls)), 1, calls)
        self.assertEqual(groups(self, done), ("TSK-0001, TSK-0002", "none", "TSK-0003, TSK-0004, TSK-0005"))

    def test_the_listing_starts_at_githubs_date(self):
        """TSK-2960 criterion 2, REQ-2572: with the local clock two minutes ahead of the stand-in's `Date`, the
        listing's `since` is the `Date` of the run's first response, and both created issues are read back. The
        stand-in lists only the issues written at or after `since`, so a `since` taken from the local clock reads
        neither back."""
        root, done = self.five({"responses": {"POST repos/o/r/issues": [None, None, self.REFUSED]}}, skew=120)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        first = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(START - 120))
        self.assertEqual(listings(self.calls(root)), [first])
        self.assertEqual(groups(self, done)[:2], ("TSK-0001, TSK-0002", "none"))

    def test_a_throttle_sends_no_listing(self):
        """TSK-2960 criterion 3, REQ-2572: with the third create answered by a secondary throttle, `project` sends
        no listing, names the first two tasks as created and not read back and the rest as not projected, and
        exits 3."""
        throttle = {"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY}
        root, done = self.five({"responses": {"POST repos/o/r/issues": [None, None, throttle]}})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        calls = self.calls(root)
        self.assertEqual(listings(calls), [])
        self.assertTrue(create(calls[-1]), calls)
        projected, unread, left = groups(self, done)
        self.assertEqual(projected, "none")
        self.assertEqual(re.findall(r"TSK-\d{4}", unread), ["TSK-0001", "TSK-0002"])
        self.assertEqual(re.findall(r"#\d+", unread), ["#1", "#2"])
        self.assertEqual(left, "TSK-0003, TSK-0004, TSK-0005")

    def test_an_issue_the_listing_omits_is_not_read_back(self):
        """TSK-2960 criterion 4, REQ-2572: where the listing omits a created issue, its task goes under `created, not
        read back` with what the listing showed, and the task keeps `issue:`."""
        root = Project.repository(self)
        self.stand_in(root, {"omit": [2]})
        done = self.meow_github(root, "project", "EPC-0001", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertEqual(len(listings(self.calls(root))), 1)
        projected, unread, left = groups(self, done)
        self.assertEqual((projected, left), ("TSK-0001", "none"))
        self.assertEqual(unread, "TSK-0002 (issue #2, not in the listing)")
        self.assertIn("\nissue: 2\n", Project.task(self, root, "TSK-0002-second.md"))

    def test_created_issues_are_read_back_in_one_listing(self):
        """TSK-2960 criterion 5, REQ-2572: with five tasks and every create answered, the stand-in records one
        read-back listing and no read of a single created issue, and the report holds no `partial:` line."""
        root, done = self.five({})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = self.calls(root)
        self.assertEqual(len([c for c in calls if create(c)]), 5, calls)
        self.assertEqual(len(listings(calls)), 1, calls)
        single = [c for c in calls if re.fullmatch(r"repos/o/r/issues/\d+", c["args"][1])]
        self.assertEqual(single, [], calls)
        self.assertEqual([line for line in done.stdout.splitlines() if line.startswith("partial:")], [])
        read = [line for line in done.stdout.splitlines() if line.endswith(", read back")]
        self.assertEqual(len(read), 5, done.stdout)


class Credential(Layered, unittest.TestCase):
    """ADR-1810: every run names the credential's form, read from whether a variable is set, never its value."""

    def test_the_first_line_names_the_form(self):
        """TSK-2950 criterion 4, REQ-2582: `GH_TOKEN` set, then only `GITHUB_TOKEN` set, then neither, name
        `GH_TOKEN from the environment`, `GITHUB_TOKEN from the environment` and `gh's stored credential` on the
        first line of `project`'s report, `GH_TOKEN` winning where both are set, and `GITHUB_ACTIONS=true` adds
        `, inside a GitHub Actions workflow`."""
        cases = (({"GH_TOKEN": "x"}, FORMS["GH_TOKEN"]), ({"GH_TOKEN": "x", "GITHUB_TOKEN": "y"}, FORMS["GH_TOKEN"]),
                 ({"GITHUB_TOKEN": "y"}, FORMS["GITHUB_TOKEN"]), ({}, FORMS[None]))
        for variables, form in cases:
            for actions in (False, True):
                with self.subTest(variables=sorted(variables), actions=actions):
                    root = Project.repository(self)
                    self.stand_in(root, {})
                    credential = dict(variables, **({"GITHUB_ACTIONS": "true"} if actions else {}))
                    done = self.meow_github(root, "project", "EPC-0001", "o/r", credential=credential)
                    first = (done.stdout.splitlines() or [""])[0]
                    self.assertIn(form + (ACTIONS if actions else ""), first, done.stdout + done.stderr)
                    if not actions:
                        self.assertNotIn("GitHub Actions", first)

    def test_the_token_value_is_never_printed(self):
        """TSK-2950 criterion 5, REQ-2582: a sentinel value in `GH_TOKEN` or `GITHUB_TOKEN` appears nowhere in the
        standard output or standard error of `project` or `history`. Each run is also read for the form it names,
        on `project`'s first line and in `history`'s `credential`, so the output that could carry the value is
        there to be read and a run naming no credential doesn't pass for one that keeps it out."""
        for variable in ("GH_TOKEN", "GITHUB_TOKEN"):
            for command in ("project", "history"):
                with self.subTest(variable=variable, command=command):
                    root = Project.repository(self)
                    self.stand_in(root, {"listings": SINGLE_PAGES})
                    args = ("project", "EPC-0001", "o/r") if command == "project" else ("history", "o/r")
                    done = self.meow_github(root, *args, credential={variable: SENTINEL})
                    self.assertNotIn(SENTINEL, done.stdout, "the token's value is on standard output")
                    self.assertNotIn(SENTINEL, done.stderr, "the token's value is on standard error")
                    if command == "project":
                        self.assertIn(FORMS[variable], (done.stdout.splitlines() or [""])[0], done.stdout)
                    else:
                        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                        self.assertEqual(json.loads(done.stdout).get("credential"), FORMS[variable], done.stdout)


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
