# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every check and failure path SPC-1070 states, and ADR-1100's checks.

Each fixture writes a small record that every check passes into a temporary
repository, plants one defect, and runs the launcher there. `MEOW_METHOD_BIN`
names the launcher to test, so the same fixtures can first run against a
program that returns nothing and be seen failing (REQ-2072).
"""

import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_METHOD_BIN", UNIT / "bin" / "meow-method"))


def record(kind, ident, fields, sections, body=""):
    lines = ["---", f"id: {ident}", f"artifact: {kind}", f"status: {fields.pop('status', 'approved')}",
             "revised: 2026-01-01"]
    lines += [f"{key}: {value}" for key, value in fields.items()]
    lines += ["---", "", f"# {ident}", ""]
    for section in sections:
        lines += [f"## {section}", "", "Text.", ""]
    return "\n".join(lines) + body


def index(ident, names):
    return f"---\nid: {ident}\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n# Index\n\n" + \
        "".join(f"- {name}\n" for name in names)


CLEAN = {
    "vision.md": "---\nid: vision\nartifact: vision\nstatus: live\nrevised: 2026-01-01\n---\n\n# Vision\n",
    "README.md": index("index", ["SPC-0001", "EPC-0001", "BUG-0001"]),
    "specs/SPC-0001-a-part.md": record(
        "spec", "SPC-0001", {"status": "live", "states": "[REQ-0001]", "checked-at": ""},
        ["Scope", "Boundary", "Behaviour", "Failure paths"]),
    "research/RES-0001-synthesis.md": record(
        "research", "RES-0001", {}, ["Summary", "Conclusions", "Sources"], "\nIt indexes RES-0002.\n"),
    "research/RES-0002-a-finding.md": record(
        "research", "RES-0002", {"elaborates": "RES-0001"}, ["Summary", "Method", "Conclusions", "Sources"]),
    "requirements/README.md": index("index", ["REQ-0001"]),
    "requirements/REQ-0001-an-obligation.md": record(
        "requirement", "REQ-0001",
        {"topic": "a", "class": "functional", "verification": "static", "elaborates": "RES-0002"}, []),
    "adrs/README.md": index("index", ["ADR-0001"]),
    "adrs/ADR-0001-a-choice.md": record(
        "adr", "ADR-0001", {"addresses": "[REQ-0001]"},
        ["Decision", "Why", "Alternatives", "Consequences", "What it costs"]),
    "epics/EPC-0001-a-plan.md": record(
        "epic", "EPC-0001", {"realises": "ADR-0001", "checked-at": ""},
        ["Acceptance criteria", "Tasks", "Coverage", "Not covered"]),
    "tasks/TSK-0001-a-task.md": record(
        "task", "TSK-0001", {"epic": "EPC-0001", "closes": "\n  [\n    REQ-0001,\n  ]"},
        ["What to do", "Depends on", "Evidence", "Left alone"], "\nSee [the plan](../epics/EPC-0001-a-plan.md).\n"),
    "bugs/BUG-0001-a-defect.md": record(
        "bug", "BUG-0001", {"violates": "REQ-0001", "severity": "minor", "found": "2026-01-01"},
        ["Reproduction", "What the system does", "What it should do, and why"]),
}


class Repository:
    def __init__(self, profile=None, root="project"):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "repository"
        self.path.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.path, check=True)
        if profile is not None:
            (self.path / ".meowpaw").mkdir()
            (self.path / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")
        self.root = (self.path / root).resolve() if not Path(root).is_absolute() else Path(root)
        for name, text in CLEAN.items():
            self.write(name, text)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def edit(self, name, old, new):
        path = self.root / name
        text = path.read_text(encoding="utf-8")
        assert old in text, (name, old)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def run(self, *args):
        return subprocess.run([str(BIN), *args], cwd=self.path, capture_output=True, text=True)


class Checks(unittest.TestCase):
    def repo(self, **kwargs):
        repository = Repository(**kwargs)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def found(self, done, check, line):
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(line, done.stdout)
        self.assertIn(f"{check}: 1 finding\n", done.stdout)

    def test_a_clean_record_passes_every_check(self):
        done = self.repo().run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        for check in ("front-matter", "identifiers", "relations", "index", "coverage", "shape"):
            self.assertIn(f"{check}: 0 findings", done.stdout)

    def test_front_matter_reports_a_status_outside_the_vocabulary(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")
        self.found(repository.run("check"), "front-matter",
                   "project/tasks/TSK-0001-a-task.md:4: status done is not one a task stores")

    def test_two_findings_are_counted_in_the_plural(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("front-matter: 2 findings\n", done.stdout)

    def test_a_defect_may_name_no_requirement(self):
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "violates: REQ-0001\n", "")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_front_matter_reports_a_missing_field(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]\n", "")
        done = repository.run("check", "front-matter")
        self.found(done, "front-matter", "project/adrs/ADR-0001-a-choice.md: front matter has no addresses")

    def test_identifiers_reports_a_name_and_id_that_disagree(self):
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "id: BUG-0001", "id: BUG-0002")
        self.found(repository.run("check", "identifiers"), "identifiers",
                   "project/bugs/BUG-0001-a-defect.md:2: declares id BUG-0002, where its name says BUG-0001")

    def test_identifiers_reports_a_cited_requirement_with_no_file(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nIt meets REQ-0999.")
        self.found(repository.run("check", "identifiers"), "identifiers",
                   "project/tasks/TSK-0001-a-task.md:25: cites REQ-0999, which has no file")

    def test_relations_reports_an_identifier_that_does_not_resolve(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: ADR-0001, ADR-0009")
        self.found(repository.run("check", "relations"), "relations",
                   "project/epics/EPC-0001-a-plan.md:6: realises names ADR-0009, which has no file")

    def test_relations_reports_a_link_whose_target_is_missing(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "EPC-0001-a-plan.md", "EPC-0001-gone.md")
        self.found(repository.run("check", "relations"), "relations",
                   "project/tasks/TSK-0001-a-task.md:31: links to ../epics/EPC-0001-gone.md, which doesn't exist")

    def test_index_reports_an_artifact_its_index_does_not_list(self):
        repository = self.repo()
        repository.write("requirements/README.md", index("index", []))
        self.found(repository.run("check", "index"), "index",
                   "project/requirements/README.md: doesn't list REQ-0001")

    def test_index_reports_an_entry_with_no_file(self):
        repository = self.repo()
        repository.write("adrs/README.md", index("index", ["ADR-0001", "ADR-0002"]))
        self.found(repository.run("check", "index"), "index",
                   "project/adrs/README.md:11: lists ADR-0002, which has no file")

    def test_coverage_reports_a_requirement_in_no_task(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "REQ-0001,", "")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/epics/EPC-0001-a-plan.md: REQ-0001 lands in no task")

    def test_coverage_reports_a_requirement_no_specification_states(self):
        repository = self.repo()
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/adrs/ADR-0001-a-choice.md: REQ-0001 is stated in no specification")

    def test_shape_reports_research_without_its_conclusions(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Conclusions", "## Thoughts")
        self.found(repository.run("check", "shape"), "shape",
                   "project/research/RES-0002-a-finding.md: has no Conclusions section")

    def test_a_file_of_no_known_kind_is_reported(self):
        repository = self.repo()
        repository.write("notes/stray.md", "---\nid: x\nartifact: note\nstatus: live\nrevised: 2026-01-01\n---\n")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/notes/stray.md: an artifact of no known kind")


class Where(unittest.TestCase):
    def test_a_root_outside_the_repository_is_read_there(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        elsewhere = Path(outside.name) / "record"
        repository = Repository(profile=f'[record]\nroot = "{elsewhere}"\n', root=str(elsewhere))
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(f"{elsewhere.resolve()}/tasks/TSK-0001-a-task.md:4: status done", done.stdout)
        self.assertFalse((repository.path / "project").exists())

    def test_a_relative_root_leading_outside_is_read_there(self):
        repository = Repository(profile='[record]\nroot = "../shared/record"\n', root="../shared/record")
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("shape: 0 findings", done.stdout)

    def test_a_root_that_does_not_exist_checks_nothing(self):
        repository = Repository(profile='[record]\nroot = "nowhere"\n')
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("nowhere doesn't exist; nothing was checked", done.stdout)
        self.assertNotIn("findings", done.stdout)

    def test_an_unknown_check_names_the_six(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("check", "spelling")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("front-matter, identifiers, relations, index, coverage, shape", done.stderr)


class NoWrites(unittest.TestCase):
    def test_the_tree_is_identical_before_and_after_a_run(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")

        def tree():
            out = {}
            for path in sorted(repository.path.rglob("*")):
                if ".git" in path.parts:
                    continue
                stat = path.stat()
                digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir"
                out[str(path)] = (digest, stat.st_mtime_ns)
            return out

        before = tree()
        done = repository.run("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(before, tree())


if __name__ == "__main__":
    unittest.main()
