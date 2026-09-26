# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every check and failure path SPC-1070 states, and ADR-1100's checks.

Each fixture writes a small record that every check passes into a temporary
repository, plants one defect, and runs the launcher there. `MEOW_METHOD_BIN`
names the launcher to test, so the same fixtures can first run against a
program that returns nothing and be seen failing (REQ-2072).
"""

import hashlib
import re
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
        ["Decision", "Why", "Alternatives", "What it costs", "What would reverse it", "Consequences"]),
    "epics/EPC-0001-a-plan.md": record(
        "epic", "EPC-0001", {"realises": "ADR-0001", "checked-at": ""},
        ["Acceptance criteria", "Tasks", "Coverage", "Not covered"]),
    "tasks/TSK-0001-a-task.md": record(
        "task", "TSK-0001", {"epic": "EPC-0001", "closes": "\n  [\n    REQ-0001,\n  ]"},
        ["What to do", "Depends on", "Evidence", "Left alone"], "\nSee [the plan](../epics/EPC-0001-a-plan.md).\n"),
    "bugs/BUG-0001-a-defect.md": record(
        "bug", "BUG-0001", {"violates": "REQ-0001", "severity": "minor", "found": "2026-01-01"},
        ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"]),
}

CLEAN["adrs/ADR-0001-a-choice.md"] = CLEAN["adrs/ADR-0001-a-choice.md"].replace(
    "## Alternatives\n\nText.", "## Alternatives\n\n| Option | Why it lost |\n| ------ | ----------- |\n| Nothing | It costs more |")


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
        for check in ("front-matter", "identifiers", "relations", "index", "coverage", "shape", "rules"):
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
        self.assertIn("front-matter: 0 findings", done.stdout)

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

    def test_a_relation_is_bare_identifiers(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "elaborates: RES-0002",
                        "elaborates: [RES-0002](../research/RES-0002-a-finding.md)")
        self.found(repository.run("check", "relations"), "relations",
                   "project/requirements/REQ-0001-an-obligation.md:9: elaborates holds more than bare identifiers")

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

    def test_a_draft_decision_carries_the_drafts_sections_and_an_approved_one_not(self):
        repository = self.repo()
        self.assertEqual(repository.run("check", "shape").returncode, 0)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        done = repository.run("check", "shape")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/ADR-0001-a-choice.md: has no How I will know it was realised section, "
                      "which a draft decision carries", done.stdout)
        self.assertIn("has no What this does not settle section", done.stdout)

    def test_research_opens_with_its_summary(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Summary\n\nText.\n\n## Method", "## Method\n\nText.\n\n## Summary")
        self.found(repository.run("check", "shape"), "shape",
                   "project/research/RES-0002-a-finding.md: opens with Method, where a research opens with Summary")

    def test_research_carries_a_method_and_its_index_is_exempt(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Method\n\nText.\n\n", "")
        done = repository.run("check", "shape")
        self.found(done, "shape", "project/research/RES-0002-a-finding.md: has no Method section, which a research carries")
        self.assertNotIn("RES-0001", done.stdout)

    def test_a_requirement_never_carries_a_priority(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "topic: a", "topic: a\npriority: high")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/requirements/REQ-0001-an-obligation.md:7: carries priority, which a requirement never does")

    def test_a_decision_must_address_a_requirement(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: []")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/ADR-0001-a-choice.md:6: addresses is empty, and a decision must fill it", done.stdout)

    def test_a_defect_carries_its_triage_and_no_priority(self):
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "## Triage", "## Thoughts")
        self.found(repository.run("check", "shape"), "shape",
                   "project/bugs/BUG-0001-a-defect.md: has no Triage section, which a defect carries")
        repository.edit("bugs/BUG-0001-a-defect.md", "severity: minor", "severity: minor\npriority: p1")
        self.assertIn("carries priority, which a defect never does", repository.run("check", "front-matter").stdout)

    def test_the_living_vision_stores_only_live(self):
        repository = self.repo()
        repository.edit("vision.md", "status: live", "status: approved")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/vision.md:4: status approved is not one a vision stores: live")

    def test_an_observed_status_is_never_stored(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "status: approved", "status: verified")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/epics/EPC-0001-a-plan.md:4: status verified is not one a epic stores")

    def test_a_numbered_kind_is_named_for_its_identifier(self):
        repository = self.repo()
        repository.write("research/a-loose-note.md", CLEAN["research/RES-0002-a-finding.md"].replace("RES-0002", "RES-0003"))
        done = repository.run("check", "identifiers")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/research/a-loose-note.md: the name doesn't have the form RES-NNNN-<slug>.md", done.stdout)

    def test_a_research_draft_dates_each_source_and_an_approved_one_need_not(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Sources\n\nText.",
                        "## Sources\n\n- [A page](https://example.org), read 2026-01-01\n- [Another](https://example.org)")
        self.assertEqual(repository.run("check", "rules").returncode, 0)
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.found(repository.run("check", "rules"), "rules",
                   "project/research/RES-0002-a-finding.md:26: names a source without the date it was read")

    def test_a_research_draft_cites_no_requirement(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Method\n\nText.", "## Method\n\nAs REQ-0001 asks.")
        self.assertEqual(repository.run("check", "rules").returncode, 0)
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.found(repository.run("check", "rules"), "rules",
                   "project/research/RES-0002-a-finding.md:17: cites REQ-0001, and research cites no requirement")

    def test_a_judged_requirement_draft_names_its_verifier(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", "verification: judgement")
        self.assertEqual(repository.run("check", "rules").returncode, 0)
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: draft")
        self.found(repository.run("check", "rules"), "rules",
                   "project/requirements/REQ-0001-an-obligation.md:8: is verified by judgement and names no verifier")
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: judgement", "verification: judgement\nverifier: agent")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_an_epic_realises_exactly_one_record(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: ADR-0001, BUG-0001")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:6: realises 2 records, where an epic realises exactly one decision or defect")

    def test_a_decision_says_why_each_alternative_lost(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "| Option | Why it lost |", "| Option | Notes |")
        self.found(repository.run("check", "rules"), "rules",
                   "project/adrs/ADR-0001-a-choice.md:21: has no column saying why each alternative lost")

    def mark(self, repository, mark, extra=""):
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        f"## Tasks\n\n- [{mark}] T-001 TSK-0001 the task\n      closes: REQ-0001{extra}")

    def test_a_task_marked_done_carries_evidence(self):
        repository = self.repo()
        self.mark(repository, "x")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.found(repository.run("check", "rules"), "rules",
                   'project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 done, and its Evidence section holds nothing past "Not yet."')
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nNot yet.", "## Evidence\n\nNot yet.\n\nThe fixture passed.")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_task_with_evidence_left_unmarked_is_reported(self):
        repository = self.repo()
        self.mark(repository, " ")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/epics/EPC-0001-a-plan.md:18: leaves TSK-0001 unmarked, and its Evidence section is written")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet. Postponed by the owner.")
        self.assertEqual(repository.run("check", "coverage").returncode, 0)

    def test_a_task_closing_a_withdrawn_requirement_in_an_open_epic_is_reported(self):
        repository = self.repo()
        self.mark(repository, "x")
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/tasks/TSK-0001-a-task.md:7: closes REQ-0001, which is withdrawn, in EPC-0001, which is not verified")
        repository.edit("epics/EPC-0001-a-plan.md", 'checked-at: ', 'checked-at: "#1"')
        self.assertEqual(repository.run("check", "coverage").returncode, 0)

    def test_a_draft_body_naming_a_missing_identifier_is_reported(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        repository.edit("tasks/TSK-0001-a-task.md", "## Left alone\n\nText.", "## Left alone\n\nADR-0009 and `ADR-0008`.\n\n```text\nADR-0007\n```")
        done = repository.run("check", "relations")
        self.found(done, "relations", "project/tasks/TSK-0001-a-task.md:29: names ADR-0009, which has no file")
        self.assertNotIn("ADR-0008", done.stdout)
        self.assertNotIn("ADR-0007", done.stdout)
        repository.edit("tasks/TSK-0001-a-task.md", "status: draft", "status: approved")
        self.assertEqual(repository.run("check", "relations").returncode, 0)

    def test_a_task_added_after_approval_says_why(self):
        repository = self.repo()
        self.mark(repository, "+")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 added after approval with no added: line saying why")
        repository.edit("epics/EPC-0001-a-plan.md", "closes: REQ-0001", "closes: REQ-0001\n      added: nobody foresaw the case")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_dropped_task_keeps_its_entry_and_says_why(self):
        repository = self.repo()
        self.mark(repository, "~")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 dropped with no dropped: line saying why")
        repository.edit("epics/EPC-0001-a-plan.md", "closes: REQ-0001", "closes: REQ-0001\n      dropped: the decision was reversed")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_draft_task_carries_acceptance_criteria(self):
        repository = self.repo()
        self.assertEqual(repository.run("check", "shape").returncode, 0)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        self.found(repository.run("check", "shape"), "shape",
                   "project/tasks/TSK-0001-a-task.md: has no Acceptance criteria section, which a draft task carries")

    def test_a_file_of_no_known_kind_is_reported(self):
        repository = self.repo()
        repository.write("notes/stray.md", "---\nid: x\nartifact: note\nstatus: live\nrevised: 2026-01-01\n---\n")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/notes/stray.md: an artifact of no known kind")


class Chain(unittest.TestCase):
    """SPC-1090: the gate each step checks, the chain's state, and the template in force."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def mark(self, repository, mark):
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        f"## Tasks\n\n- [{mark}] T-001 TSK-0001 the task\n      closes: REQ-0001")

    def ready(self, repository, *args):
        return repository.run("ready", *args)

    def test_research_is_always_ready(self):
        done = self.ready(self.repo(), "research")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("research needs no approved input", done.stdout)

    def test_design_refuses_a_draft_requirement_and_names_it(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: draft")
        done = self.ready(repository, "design", "REQ-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("REQ-0001, a requirement, is draft and not approved", done.stdout)
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: draft", "status: approved")
        self.assertEqual(self.ready(repository, "design", "REQ-0001").returncode, 0)

    def test_requirements_and_spec_refuse_what_has_no_file(self):
        repository = self.repo()
        for step, missing in (("requirements", "RES-0009"), ("spec", "ADR-0009")):
            done = self.ready(repository, step, missing)
            self.assertEqual(done.returncode, 1, step)
            self.assertIn(f"{missing} has no file", done.stdout, step)
        self.assertEqual(self.ready(repository, "requirements", "RES-0002").returncode, 0)
        self.assertEqual(self.ready(repository, "spec", "ADR-0001").returncode, 0)

    def test_epic_refuses_a_decision_whose_requirement_no_spec_states(self):
        repository = self.repo()
        self.assertEqual(self.ready(repository, "epic", "ADR-0001").returncode, 0)
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        done = self.ready(repository, "epic", "ADR-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("REQ-0001, which ADR-0001 addresses, is stated by no specification", done.stdout)

    def test_implement_refuses_until_its_dependency_is_done(self):
        repository = self.repo()
        repository.write("tasks/TSK-0002-a-second-task.md", CLEAN["tasks/TSK-0001-a-task.md"]
                         .replace("TSK-0001", "TSK-0002").replace("## Depends on\n\nText.", "## Depends on\n\nTSK-0001."))
        self.mark(repository, " ")
        done = self.ready(repository, "implement", "TSK-0002")
        self.assertEqual(done.returncode, 1)
        self.assertIn("TSK-0001, which TSK-0002 depends on, isn't done", done.stdout)
        self.mark_done(repository)
        self.assertEqual(self.ready(repository, "implement", "TSK-0002").returncode, 0)

    def mark_done(self, repository):
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")

    def test_implement_refuses_a_task_whose_epic_is_a_draft(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "status: approved", "status: draft")
        done = self.ready(repository, "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("EPC-0001, the epic of TSK-0001, is draft and not approved", done.stdout)

    def test_document_and_verify_wait_for_every_task(self):
        repository = self.repo()
        self.mark(repository, " ")
        for step in ("document", "verify"):
            done = self.ready(repository, step, "EPC-0001")
            self.assertEqual(done.returncode, 1, step)
            self.assertIn("TSK-0001, a task of EPC-0001, isn't done", done.stdout, step)
        self.mark_done(repository)
        for step in ("document", "verify"):
            self.assertEqual(self.ready(repository, step, "EPC-0001").returncode, 0, step)

    def test_review_waits_for_verification(self):
        repository = self.repo()
        done = self.ready(repository, "review", "EPC-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("EPC-0001 hasn't been verified", done.stdout)
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#1"')
        self.assertEqual(self.ready(repository, "review", "EPC-0001").returncode, 0)

    def test_an_unknown_step_names_the_nine(self):
        done = self.ready(self.repo(), "deploy", "EPC-0001")
        self.assertEqual(done.returncode, 2)
        self.assertIn("research, requirements, design, spec, epic, implement, document, verify, review", done.stderr)

    def test_status_leads_with_drafts_and_places_each_decision(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.mark(repository, " ")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "Waiting for approval")
        self.assertIn("RES-0002 research, draft", lines[1])
        self.assertIn("next: implement TSK-0001 (EPC-0001, 0 of 1 task done)", done.stdout)
        self.mark_done(repository)
        self.assertIn("next: document, then verify EPC-0001 (1 task done)", repository.run("status").stdout)
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#7"')
        self.assertIn("realised: EPC-0001 verified under #7", repository.run("status").stdout)

    def test_status_places_a_decision_with_no_epic(self):
        repository = self.repo()
        (repository.root / "epics" / "EPC-0001-a-plan.md").unlink()
        self.assertIn("next: spec, then epic", repository.run("status").stdout)

    def test_status_prints_the_same_state_twice(self):
        repository = self.repo()
        first = repository.run("status").stdout
        self.assertIn("ADR-0001", first)
        self.assertEqual(first, repository.run("status").stdout)

    def test_template_prefers_the_repository_own(self):
        repository = self.repo()
        unit = UNIT / "templates" / "task.md"
        done = repository.run("template", "task")
        if unit.is_file():
            self.assertEqual(done.stdout.strip(), str(unit))
        else:
            self.assertEqual(done.returncode, 1)
        own = repository.path / ".meowpaw" / "templates" / "task.md"
        own.parent.mkdir(parents=True)
        own.write_text("# mine\n", encoding="utf-8")
        done = repository.run("template", "task")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(Path(done.stdout.strip()).resolve(), own.resolve())

    def test_an_unknown_kind_names_the_kinds(self):
        done = self.repo().run("template", "memo")
        self.assertEqual(done.returncode, 2)
        self.assertIn("research, requirement, adr, spec, epic, task, bug, vision, constitution", done.stderr)


class Show(unittest.TestCase):
    """SPC-1100: an identifier resolves to its artifact and to what cites it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_show_resolves_an_identifier_and_derives_what_cites_it(self):
        done = self.repo().run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "REQ-0001 requirement, approved: project/requirements/REQ-0001-an-obligation.md")
        self.assertIn("Names\n  elaborates: RES-0002", done.stdout)
        cited = done.stdout.split("Cited by\n", 1)[1]
        for line in ("  addresses: ADR-0001", "  closes: TSK-0001", "  states: SPC-0001", "  violates: BUG-0001",
                     "  body: project/requirements/README.md"):
            self.assertIn(line, cited)

    def test_a_withdrawn_artifact_still_resolves(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0)
        self.assertIn("REQ-0001 requirement, withdrawn:", done.stdout)

    def test_an_identifier_with_no_artifact_resolves_to_nothing(self):
        done = self.repo().run("show", "REQ-0999")
        self.assertEqual(done.returncode, 1)
        self.assertIn("REQ-0999 resolves to nothing in the record", done.stdout)

    def test_show_needs_an_identifier(self):
        done = self.repo().run("show")
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage: meow-method show <id>", done.stderr)


class Frozen(unittest.TestCase):
    """ADR-1170: an approved record changed since a base, outside what its kind may change."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        return repository

    def frozen(self, repository):
        return repository.run("check", "frozen", "--base", "HEAD")

    def test_nothing_changed_is_clean(self):
        done = self.frozen(self.repo())
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_rewording_an_approved_requirement_invalidates_it(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001", "# REQ-0001\n\nThe system MUST do more.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/requirements/REQ-0001-an-obligation.md: approved at HEAD, and changed since", done.stdout)

    def test_a_change_naming_its_authority_passes(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001", "# REQ-0001\n\n**Amended by ADR-0001.** It says more.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_task_may_gain_evidence_and_an_unverified_epic_marks(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nThe fixture passed.")
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [x] T-001 TSK-0001 the task")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_task_rewritten_outside_its_evidence_is_reported(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## What to do\n\nText.", "## What to do\n\nSomething else.")
        self.assertEqual(self.frozen(repository).returncode, 1)

    def test_a_verified_epic_is_frozen(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#9"')
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\nTidied.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/epics/EPC-0001-a-plan.md: approved at HEAD", done.stdout)

    def test_a_living_document_is_never_frozen(self):
        repository = self.repo()
        repository.edit("specs/SPC-0001-a-part.md", "## Scope\n\nText.", "## Scope\n\nRewritten.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_kinds_own_index_is_never_frozen(self):
        repository = self.repo()
        repository.edit("research/RES-0001-synthesis.md", "It indexes RES-0002.", "It indexes RES-0002, and more.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_withdrawing_a_requirement_passes(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)


class Waiting(unittest.TestCase):
    """ADR-1170: a session opens with what waits for approval, and says nothing otherwise."""

    def test_a_draft_decision_is_reported_at_its_gate(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        done = repository.run("status", "--waiting")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("ADR-0001 decision, at the design gate", done.stdout)

    def test_nothing_waiting_prints_nothing(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("status", "--waiting")
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertIn("ADR-0001", repository.run("status").stdout)

    def test_a_repository_with_no_record_prints_nothing(self):
        repository = Repository(profile='[record]\nroot = "nowhere"\n')
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("status", "--waiting")
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertIn("nowhere", repository.run("status").stdout)


class Indexes(unittest.TestCase):
    """ADR-1180: a kind's index generated from the tree, and checked for drift."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "---\nid: index\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n"
                         "# Decisions\n\nWritten by hand.\n\n<!-- meow-method index -->\n<!-- /meow-method index -->\n")
        return repository

    def test_index_writes_the_block_and_keeps_the_prose(self):
        repository = self.repo()
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        text = (repository.root / "adrs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Written by hand.", text)
        self.assertIn("| [ADR-0001](ADR-0001-a-choice.md) |", text)
        self.assertIn("1 decision in all: 1 approved.", text)
        self.assertEqual(repository.run("check", "index").returncode, 0)

    def test_an_index_left_behind_is_reported_and_rewriting_clears_it(self):
        repository = self.repo()
        repository.run("index", "adr", "--write")
        repository.write("adrs/ADR-0002-another.md", CLEAN["adrs/ADR-0001-a-choice.md"].replace("ADR-0001", "ADR-0002"))
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/README.md:12: its generated block is out of date; run meow-method index decision --write",
                      done.stdout)
        repository.run("index", "adr", "--write")
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("index: 0 findings", done.stdout)

    def test_padding_a_generated_table_is_not_drift(self):
        repository = self.repo()
        repository.run("index", "adr", "--write")
        path = repository.root / "adrs" / "README.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| --- |", "| ------------ |").replace("| [ADR", "|   [ADR"),
                        encoding="utf-8")
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("index: 0 findings", done.stdout)

    def test_a_large_kind_gains_a_view_by_topic_ordered_by_identifier(self):
        repository = self.repo()
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        for n in range(2, 40):
            topic = "b" if n % 2 else "a"
            repository.write(f"requirements/REQ-{n:04d}-r.md",
                             base.replace("REQ-0001", f"REQ-{n:04d}").replace("topic: a", f"topic: {topic}"))
        done = repository.run("index", "requirement")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        rows = re.findall(r"^\| \[(REQ-\d{4})\]", done.stdout, re.M)
        self.assertEqual(rows, sorted(rows))
        self.assertEqual(len(rows), 39)
        self.assertIn("By topic:", done.stdout)
        self.assertRegex(done.stdout, r"- a: REQ-0001, REQ-0002, REQ-0004")


class Allocate(unittest.TestCase):
    """ADR-1180: the next identifier, in its topic's block, never one already taken."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        repository.write("requirements/REQ-0010-ten.md", base.replace("REQ-0001", "REQ-0010").replace("topic: a", "topic: t"))
        return repository

    def new(self, repository, *args):
        done = repository.run("new", *args)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return done.stdout.strip()

    def test_a_requirement_takes_the_next_number_in_its_topic(self):
        repository = self.repo()
        self.assertEqual(self.new(repository, "requirement", "--topic", "t"), "REQ-0012")
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        repository.write("requirements/REQ-0012-twelve.md", base.replace("REQ-0001", "REQ-0012").replace("topic: a", "topic: t"))
        self.assertEqual(self.new(repository, "requirement", "--topic", "t"), "REQ-0014")

    def test_a_withdrawn_or_cited_number_is_never_given_again(self):
        repository = self.repo()
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        repository.write("requirements/REQ-0012-gone.md", base.replace("REQ-0001", "REQ-0012").replace("topic: a", "topic: z")
                         .replace("status: approved", "status: withdrawn"))
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nSee REQ-0014.")
        self.assertEqual(self.new(repository, "requirement", "--topic", "t"), "REQ-0016")

    def test_a_new_topic_starts_a_block_above_the_highest(self):
        self.assertEqual(self.new(self.repo(), "requirement", "--topic", "fresh"), "REQ-0100")

    def test_other_kinds_take_the_next_block_of_ten(self):
        repository = self.repo()
        self.assertEqual(self.new(repository, "adr"), "ADR-0010")
        self.assertEqual(self.new(repository, "research"), "RES-0003")

    def test_a_requirement_needs_its_topic(self):
        done = self.repo().run("new", "requirement")
        self.assertEqual(done.returncode, 2)
        self.assertIn("name it with --topic", done.stderr)


class Find(unittest.TestCase):
    """ADR-1180: identifiers and headings first, ranked by the words matched."""

    def test_find_ranks_and_prints_headings_only(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("adrs/ADR-0001-a-choice.md", "# ADR-0001", "# 0001. An approval gate for the plan")
        repository.edit("epics/EPC-0001-a-plan.md", "# EPC-0001", "# The gate")
        done = repository.run("find", "approval", "gate")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[0], "ADR-0001 decision, approved: An approval gate for the plan")
        self.assertEqual(lines[1], "EPC-0001 epic, approved: The gate")
        self.assertNotIn("Text.", done.stdout)

    def test_find_with_no_match_says_so(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("find", "zebra")
        self.assertEqual(done.returncode, 1)
        self.assertIn("nothing in the record carries zebra", done.stdout)

    def test_find_needs_a_word(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("find")
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage: meow-method find", done.stderr)


class ReadOnly(unittest.TestCase):
    """ADR-1200: the commands that read the record write nothing, and repeat themselves."""

    COMMANDS = (["check"], ["check", "frozen"], ["status"], ["status", "--waiting"], ["ready", "design", "REQ-0001"],
                ["template", "task"], ["show", "REQ-0001"], ["index", "requirement"], ["new", "adr"],
                ["find", "task"])

    def tree(self, root):
        out = {}
        for path in sorted(root.rglob("*")):
            if ".git" in path.parts:
                continue
            stat = path.stat()
            out[str(path)] = (hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir", stat.st_mtime_ns)
        return out

    def test_each_read_only_command_writes_nothing_and_repeats_itself(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        for command in self.COMMANDS:
            before = self.tree(repository.path)
            first = repository.run(*command)
            second = repository.run(*command)
            self.assertEqual(before, self.tree(repository.path), command)
            self.assertEqual(first.stdout, second.stdout, command)
            # Nothing waiting is the one case whose right answer is silence.
            if command != ["status", "--waiting"]:
                self.assertNotEqual(first.stdout + first.stderr, "", command)

    def test_writing_an_index_leaves_no_temporary_file(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "# Decisions\n\n<!-- meow-method index -->\n<!-- /meow-method index -->\n")
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(sorted(p.name for p in (repository.root / "adrs").iterdir()),
                         ["ADR-0001-a-choice.md", "README.md"])
        written = (repository.root / "adrs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("| [ADR-0001](ADR-0001-a-choice.md) |", written)
        self.assertIn("<!-- /meow-method index -->", written)


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
        self.assertIn("front-matter, identifiers, relations, index, coverage, shape, rules", done.stderr)


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
