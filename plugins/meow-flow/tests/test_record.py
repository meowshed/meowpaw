# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every check and failure path SPC-1070 states, and ADR-1100's checks.

Each fixture writes a small record that every check passes into a temporary
repository, plants one defect, and runs the launcher there. `MEOW_FLOW_BIN`
names the launcher to test, so the same fixtures can first run against a
program that returns nothing and be seen failing (REQ-2072).
"""

import hashlib
import re
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_FLOW_BIN", UNIT / "bin" / "paw"))


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
    "vision.md": "---\nid: vision\nartifact: vision\nstatus: live\nrevised: 2026-01-01\n---\n\n# Vision\n\n" + "".join(
        f"## {section}\n\nText.\n\n" for section in ("Who it is for", "Quality goals", "What it will not do", "Risks")),
    "README.md": index("index", ["SPC-0001", "BUG-0001"]),
    "specs/SPC-0001-a-part.md": record(
        "spec", "SPC-0001", {"status": "live", "states": "[REQ-0001]"},
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
        ["Decision", "Why", "Alternatives", "What it costs", "What would reverse it", "Consequences", "Plan"]),
    "bugs/BUG-0001-a-defect.md": record(
        "bug", "BUG-0001", {"violates": "REQ-0001", "severity": "minor", "found": "2026-01-01"},
        ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"]),
}

CLEAN["adrs/ADR-0001-a-choice.md"] = CLEAN["adrs/ADR-0001-a-choice.md"].replace(
    "## Alternatives\n\nText.", "## Alternatives\n\n| Option | Why it lost |\n| ------ | ----------- |\n| Nothing | It costs more |")


# A task `paw upgrade` archived, which a test writes where it needs one, closing `closes`.
def archived_task(closes):
    return record("task", "TSK-0001", {"status": "done", "closes": f"[{closes}]"}, ["Evidence"])


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
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: closed")
        self.found(repository.run("check"), "front-matter",
                   "project/bugs/BUG-0001-a-defect.md:4: status closed is not one a defect stores")
    def test_two_findings_are_counted_in_the_plural(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: closed")
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: closed")
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
        repository.edit("adrs/ADR-0001-a-choice.md", "## Why\n\nText.", "## Why\n\nIt meets REQ-0999.")
        self.found(repository.run("check", "identifiers"), "identifiers",
                   "project/adrs/ADR-0001-a-choice.md:17: cites REQ-0999, which has no file")
    def test_relations_reports_an_identifier_that_does_not_resolve(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001]\nsupersedes: [ADR-0009]")
        self.found(repository.run("check", "relations"), "relations",
                   "project/adrs/ADR-0001-a-choice.md:7: supersedes names ADR-0009, which has no file")
    def test_relations_reports_a_link_whose_target_is_missing(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Why\n\nText.", "## Why\n\nSee [the part](../specs/SPC-0001-gone.md).")
        self.found(repository.run("check", "relations"), "relations",
                   "project/adrs/ADR-0001-a-choice.md:17: links to ../specs/SPC-0001-gone.md, which doesn't exist")
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

    def test_a_decision_must_address_or_postpone_a_requirement(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: []")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/ADR-0001-a-choice.md:6: addresses no requirement and postpones none", done.stdout)

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
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: verified")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/adrs/ADR-0001-a-choice.md:4: status verified is not one a decision stores")
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

    def test_a_decision_says_why_each_alternative_lost(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "| Option | Why it lost |", "| Option | Notes |")
        self.found(repository.run("check", "rules"), "rules",
                   "project/adrs/ADR-0001-a-choice.md:21: has no column saying why each alternative lost")

    def test_a_draft_body_naming_a_missing_identifier_is_reported(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        repository.edit("research/RES-0002-a-finding.md", "## Method\n\nText.", "## Method\n\nADR-0009 and `ADR-0008`.\n\n```text\nADR-0007\n```")
        done = repository.run("check", "relations")
        self.found(done, "relations", "project/research/RES-0002-a-finding.md:17: names ADR-0009, which has no file")
        self.assertNotIn("ADR-0008", done.stdout)
        self.assertNotIn("ADR-0007", done.stdout)
        repository.edit("research/RES-0002-a-finding.md", "status: draft", "status: approved")
        self.assertEqual(repository.run("check", "relations").returncode, 0)
    def test_show_derives_a_requirements_state(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("State\n  closed\n  ADR-0001 done\n", done.stdout)
        repository.write("requirements/REQ-0002-another.md",
                         (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8").replace("REQ-0001", "REQ-0002"))
        self.assertIn("State\n  open, named by no decision\n\n", repository.run("show", "REQ-0002").stdout)
    def test_status_counts_requirements_by_derived_state(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        repository.write("requirements/REQ-0002-another.md",
                         (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8").replace("REQ-0001", "REQ-0002"))
        self.assertIn("Requirements\n  2 in force: 1 closed, 0 in a decision not yet done, 0 reopened by a defect, 0 postponed, 1 named by no decision\n",
                      repository.run("status").stdout)
    def test_status_says_a_record_under_no_version_control_is_local(self):
        repository = self.repo()
        self.assertNotIn("local to this machine", repository.run("status").stdout)
        shutil.rmtree(repository.path / ".git")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("The record is local to this machine: ", done.stdout)

    INSIGHT = ("---\nid: INS-0001\nartifact: insight\nstatus: approved\nrevised: 2026-01-01\n---\n\n"
               "# A cache keyed by path misses after a rename\n\nText.\n\n## Evidence\n\n41 of 50 runs missed.\n\n"
               "## What looked right\n\nNone did.\n\n## The pattern\n\nKey a cache by content.\n")

    def insight(self, old="", new=""):
        repository = self.repo()
        repository.write("insights/INS-0001-a-lesson.md", self.INSIGHT.replace(old, new, 1))
        return repository

    def test_an_insight_meeting_each_rule_passes(self):
        repository = self.insight()
        done = repository.run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("rules: 0 findings\n", done.stdout)
        self.assertTrue(repository.run("show", "INS-0001").stdout.startswith("INS-0001 insight, approved: "))

    def test_an_insight_title_states_a_claim(self):
        self.found(self.insight("A cache keyed by path misses after a rename", "Notes 2026-01-01").run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:8: has a title carrying a date, where an insight's title states its claim")
        self.found(self.insight("A cache keyed by path misses after a rename", "Caching").run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:8: has a title of 1 word, where an insight's title states its claim in at least four")

    def test_an_insight_carries_measured_evidence(self):
        self.found(self.insight("41 of 50 runs missed.", "Most runs missed.").run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:12: has evidence with no number, measurement or reproducible block")
        done = self.insight("41 of 50 runs missed.", "```text\n$ run\n```").run("check", "rules")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_an_insight_ends_with_its_pattern(self):
        repository = self.insight("## The pattern\n\nKey a cache by content.\n", "## The pattern\n\nKey a cache by content.\n\n## Notes\n\nMore.\n")
        self.found(repository.run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:24: ends with Notes, where an insight ends with The pattern")

    def test_an_insight_is_allocated_and_templated(self):
        repository = self.repo()
        self.assertEqual(repository.run("new", "insight").stdout, "INS-0001\n")
        template = repository.run("template", "insight")
        self.assertEqual(template.returncode, 0, template.stderr)
        self.assertTrue(template.stdout.strip().endswith("templates/insight.md"), template.stdout)
        self.assertIn("## The pattern", Path(template.stdout.strip()).read_text(encoding="utf-8"))

    def test_the_specifications_index_lists_each_after_what_it_cites(self):
        repository = self.repo()
        spec = (repository.root / "specs/SPC-0001-a-part.md").read_text(encoding="utf-8")
        repository.write("specs/SPC-0002-a-layer.md", spec.replace("SPC-0001", "SPC-0002"))
        repository.edit("specs/SPC-0001-a-part.md", "## Scope\n\nText.", "## Scope\n\nText, built on SPC-0002.")
        repository.edit("README.md", "- SPC-0001\n", "- SPC-0001\n- SPC-0002\n")
        self.found(repository.run("check", "index"), "index", "project/README.md:10: lists SPC-0001 before SPC-0002, which it cites")
        repository.edit("README.md", "- SPC-0001\n- SPC-0002\n", "- SPC-0002\n- SPC-0001\n")
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("index: 0 findings\n", done.stdout)

    def test_a_living_document_collects_a_withdrawn_citation(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        repository.edit("specs/SPC-0001-a-part.md", "## Behaviour\n\nText.", "## Behaviour\n\nIt holds REQ-0001.")
        self.found(repository.run("check", "shape"), "shape",
                   "project/specs/SPC-0001-a-part.md:21: cites REQ-0001, which is withdrawn, outside a Withdrawn section")
        repository.edit("specs/SPC-0001-a-part.md", "## Behaviour\n\nIt holds REQ-0001.", "## Behaviour\n\nText.")
        repository.edit("specs/SPC-0001-a-part.md", "## Failure paths\n\nText.", "## Failure paths\n\nText.\n\n## Withdrawn\n\nREQ-0001, by ADR-0001.")
        done = repository.run("check", "shape")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("shape: 0 findings\n", done.stdout)

    def test_nothing_is_kept_in_an_archive_directory(self):
        repository = self.repo()
        research = (repository.root / "research/RES-0002-a-finding.md").read_text(encoding="utf-8")
        repository.write("research/archive/RES-0003-old.md", research.replace("RES-0002", "RES-0003"))
        self.assertIn("project/research/archive/RES-0003-old.md: sits in research/archive, a directory named for an archive; "
                      "freeze the record or discard it with a reason", repository.run("check", "shape").stdout)

    def statement(self, text, status="draft"):
        repository = self.repo()
        path = repository.root / "requirements/REQ-0001-an-obligation.md"
        body = path.read_text(encoding="utf-8").replace("status: approved", f"status: {status}")
        head, _, _ = body.partition("# REQ-0001")
        repository.write("requirements/REQ-0001-an-obligation.md", head + "# REQ-0001\n\n" + text + "\n\nWhy it holds.\n")
        return repository.run("check", "rules")

    def test_a_draft_requirement_carries_one_obligation(self):
        self.found(self.statement("The check MUST run and MUST NOT write."), "rules",
                   "project/requirements/REQ-0001-an-obligation.md:14: carries more than one keyword, where a requirement carries one obligation: MUST, MUST NOT")
        self.assertEqual(self.statement("The check MUST NOT write.").returncode, 0)

    def test_a_draft_requirement_stands_alone(self):
        self.found(self.statement("Such a record MUST be kept."), "rules",
                   "project/requirements/REQ-0001-an-obligation.md:14: leans on a neighbour: Such a record")

    def test_a_draft_requirement_prohibits_with_must_not(self):
        self.found(self.statement("No step MUST write."), "rules",
                   'project/requirements/REQ-0001-an-obligation.md:14: negates a requirement with "No ... MUST", where a prohibition is MUST NOT: No step MUST')

    def test_an_approved_requirement_keeps_the_rules_it_was_approved_under(self):
        for text in ("The check MUST run and MUST NOT write.", "Such a record MUST be kept.", "No step MUST write."):
            done = self.statement(text, status="approved")
            self.assertEqual(done.returncode, 0, done.stdout)
            self.assertIn("rules: 0 findings\n", done.stdout)

    def test_a_retired_name_is_refused_in_a_record(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: proposed")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/adrs/ADR-0001-a-choice.md:4: status proposed is retired: replaced by draft")
        repository.edit("adrs/ADR-0001-a-choice.md", "status: proposed", "status: approved\nunit: meow-core")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/adrs/ADR-0001-a-choice.md:5: carries unit, a retired field: the unit of work is named by the relations the record carries")

    def test_a_retired_name_is_refused_in_the_layout(self):
        repository = self.repo()
        layout = self.tmp_layout()
        text = (UNIT / "lib" / "layout.toml").read_text(encoding="utf-8")
        layout.write_text(text.replace('statuses = ["live"]\nindex = "README.md"', 'statuses = ["live", "current"]\nindex = "README.md"', 1), encoding="utf-8")
        done = subprocess.run([str(BIN), "check", "front-matter"], cwd=repository.path, capture_output=True, text=True,
                              env={**os.environ, "MEOW_LAYOUT": str(layout)})
        self.assertIn("the layout: the kind specification declares current, a retired name\n", done.stdout)
        self.assertEqual(done.returncode, 1, done.stdout)

    def tmp_layout(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return Path(directory.name) / "layout.toml"

    def test_count_prints_each_kind_by_status_and_the_identifiers(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        first = repository.run("count")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn("requirement: 1: 1 withdrawn\n", first.stdout)
        self.assertIn("research: 1: 1 approved\n", first.stdout)
        self.assertIn("insight: 0\n", first.stdout)
        self.assertTrue(first.stdout.endswith("identifiers: 6\n"), first.stdout)
        self.assertEqual(first.stdout, repository.run("count").stdout)

    def test_an_empty_record_reports_its_coverage_as_zero(self):
        repository = self.repo()
        for path in (repository.root / "requirements").glob("REQ-*.md"):
            path.unlink()
        done = repository.run("check", "coverage")
        self.assertIn("coverage: 0 of 0 requirements in force land in a record; an empty record's coverage is zero, not complete\n", done.stdout)
        self.assertIn("Requirements\n  none in force, so coverage is zero, not complete\n", repository.run("status").stdout)

    def test_coverage_counts_the_requirements_that_land_in_a_record(self):
        done = self.repo().run("check", "coverage")
        self.assertIn("coverage: 1 of 1 requirements in force land in a record\n", done.stdout)

    REPORT = ("---\nid: onboarding\nartifact: onboarding\nstatus: draft\nrevised: 2026-01-01\n---\n\n# Onboarding\n\nText.\n\n"
              "## Verbs\n\nText.\n\n## Conventions\n\nText.\n\n## Documents\n\n"
              "| Document | Outcome | Where, or why |\n| --- | --- | --- |\n"
              "| `docs/guide.md` | migrated | SPC-0001 |\n| `notes.txt` | discarded | a scratch list nobody reads |\n\n"
              "## Gaps\n\nText.\n\n## Adoption\n\n1. Declare the verbs.\n")

    def onboarded(self, old="", new=""):
        repository = self.repo()
        (repository.path / "docs").mkdir()
        (repository.path / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        (repository.path / "notes.txt").write_text("notes\n", encoding="utf-8")
        repository.write("onboarding.md", self.REPORT.replace(old, new, 1))
        return repository

    def test_an_onboarding_report_placing_every_document_passes(self):
        done = self.onboarded().run("check", "coverage")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("coverage: 0 findings\n", done.stdout)

    def test_an_onboarding_report_places_every_document_once(self):
        self.found(self.onboarded("| `notes.txt` | discarded | a scratch list nobody reads |\n", "").run("check", "coverage"), "coverage",
                   "project/onboarding.md: doesn't place notes.txt, a document the repository has")
        self.found(self.onboarded("| `notes.txt` | discarded | a scratch list nobody reads |\n",
                                  "| `notes.txt` | discarded | a scratch list nobody reads |\n| `notes.txt` | cited | SPC-0001 |\n").run("check", "coverage"),
                   "coverage", "project/onboarding.md:26: places notes.txt 2 times")

    def test_an_onboarding_outcome_is_one_of_four_with_a_reason(self):
        self.found(self.onboarded("| `notes.txt` | discarded |", "| `notes.txt` | archived |").run("check", "coverage"), "coverage",
                   "project/onboarding.md:25: gives notes.txt the outcome archived, where an outcome is migrated, cited, superseded or discarded")
        self.found(self.onboarded("| `notes.txt` | discarded | a scratch list nobody reads |", "| `notes.txt` | discarded | |").run("check", "coverage"),
                   "coverage", "project/onboarding.md:25: marks notes.txt discarded with no destination or reason")

    def converted(self, status="approved", guide="SPC-0001"):
        repository = self.repo()
        for name in ("docs/guide.md", "notes.txt", "old.md", "source.md"):
            (repository.path / name).parent.mkdir(parents=True, exist_ok=True)
            (repository.path / name).write_text("text\n", encoding="utf-8")
        rows = (f"| `docs/guide.md` | migrated | {guide} |\n| `notes.txt` | discarded | a scratch list nobody reads |\n"
                "| `old.md` | superseded | ADR-0001 |\n| `source.md` | cited | SPC-0001 |\n")
        report = self.REPORT.replace("status: draft", f"status: {status}").replace(
            "| `docs/guide.md` | migrated | SPC-0001 |\n| `notes.txt` | discarded | a scratch list nobody reads |\n", rows)
        repository.write("onboarding.md", report)
        return repository

    def present(self, repository):
        return sorted(n for n in ("docs/guide.md", "notes.txt", "old.md", "source.md") if (repository.path / n).exists())

    def test_removing_placed_documents_keeps_what_is_cited(self):
        repository = self.converted()
        done = repository.run("onboarding", "remove")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.present(repository), ["source.md"])
        self.assertEqual(done.stdout, "before: 4 documents\nremoved docs/guide.md (migrated)\nremoved notes.txt (discarded)\n"
                                      "removed old.md (superseded)\nafter: 1 document\n")

    def test_nothing_is_removed_before_the_report_is_approved(self):
        repository = self.converted(status="draft")
        done = repository.run("onboarding", "remove")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/onboarding.md is draft, and nothing is removed before a person approves", done.stdout)
        self.assertEqual(len(self.present(repository)), 4)

    def test_nothing_is_removed_where_a_destination_does_not_exist(self):
        repository = self.converted(guide="SPC-0009")
        done = repository.run("onboarding", "remove")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("docs/guide.md is migrated to SPC-0009, which names no artifact that exists", done.stdout)
        self.assertEqual(len(self.present(repository)), 4)

    def test_onboarding_adoption_is_numbered_steps(self):
        self.found(self.onboarded("1. Declare the verbs.", "Declare the verbs.").run("check", "rules"), "rules",
                   "project/onboarding.md:31: has an Adoption section with no numbered steps, where adoption is a sequence each leaving the repository working")

    def postponing(self, fields="postpones: [REQ-0002]"):
        repository = self.repo()
        requirement = (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8")
        repository.write("requirements/REQ-0002-a-later-one.md", requirement.replace("REQ-0001", "REQ-0002"))
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        repository.write("adrs/ADR-0002-not-now.md", decision.replace("ADR-0001", "ADR-0002").replace("addresses: [REQ-0001]", f"addresses: []\n{fields}"))
        return repository

    def test_a_postponed_requirement_is_derived_and_counted(self):
        repository = self.postponing()
        shown = repository.run("show", "REQ-0002")
        self.assertIn("State\n  postponed by ADR-0002\n", shown.stdout)
        status = repository.run("status").stdout
        self.assertIn("ADR-0002", status)
        self.assertIn("postponing: 1 requirement, listed under Postponed", status)
        self.assertIn("2 in force: 0 closed, 0 in a decision not yet done, 1 reopened by a defect, 1 postponed, 0 named by no decision", status)
        for check in ("rules", "coverage"):
            done = repository.run("check", check)
            self.assertEqual(done.returncode, 0, done.stdout)

    def later_decision(self, repository, number, status):
        """A decision addressing REQ-0002, numbered before or after ADR-0002 that postpones it."""
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        repository.write(f"adrs/ADR-{number}-taken-up.md", decision.replace("ADR-0001", f"ADR-{number}").replace(
            "addresses: [REQ-0001]", "addresses: [REQ-0002]").replace("status: approved", f"status: {status}"))

    def test_a_later_decision_takes_up_a_postponed_requirement(self):
        """REQ-3680: a later decision in work opens the requirement, and closes it once it is done."""
        repository = self.postponing()
        self.later_decision(repository, "0003", "approved")
        shown = repository.run("show", "REQ-0002").stdout
        self.assertIn("State\n  open, in a decision not yet done\n", shown)
        self.assertNotIn("postponed by", shown)
        repository.edit("adrs/ADR-0003-taken-up.md", "status: approved", "status: done")
        self.assertIn("State\n  closed\n", repository.run("show", "REQ-0002").stdout)

    def test_a_decision_before_the_postponement_closes_nothing(self):
        """ADR-3090: a done decision earlier than the one that postponed the requirement leaves it postponed."""
        repository = self.postponing()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001, REQ-0002]")
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        self.assertIn("State\n  postponed by ADR-0002\n", repository.run("show", "REQ-0002").stdout)
    def test_a_decision_addressing_and_postponing_nothing_is_reported(self):
        repository = self.postponing(fields="postpones: []")
        self.found(repository.run("check", "rules"), "rules",
                   "project/adrs/ADR-0002-not-now.md:6: addresses no requirement and postpones none, where a decision does one or both")

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

    def test_implement_refuses_a_decision_whose_requirement_no_spec_states(self):
        repository = self.repo()
        self.assertEqual(self.ready(repository, "implement", "ADR-0001").returncode, 0)
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        done = self.ready(repository, "implement", "ADR-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("REQ-0001, which ADR-0001 addresses, is stated by no specification", done.stdout)
    def test_implement_refuses_a_decision_with_no_plan(self):
        """REQ-3672: the plan is what the step works through."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "\n## Plan\n\nText.\n", "\n")
        done = self.ready(repository, "implement", "ADR-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0001 carries no plan", done.stdout)
    def test_implement_refuses_a_draft_decision(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        done = self.ready(repository, "implement", "ADR-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("ADR-0001, a decision, is draft and not approved", done.stdout)

    def test_implement_takes_only_a_decision_or_a_defect(self):
        """ADR-3090: an archived task is read, and it is no input to a step."""
        repository = self.repo()
        repository.write("archive/tasks/TSK-0001-a-task.md", archived_task("REQ-0001"))
        done = self.ready(repository, "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0001 is a task, and only a decision or a defect is implemented", done.stdout)
    def test_review_needs_no_verification(self):
        """ADR-2300: nothing writes checked-at, so review doesn't wait on it."""
        done = self.ready(self.repo(), "review", "ADR-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_status_leads_with_drafts_and_places_each_decision(self):
        """REQ-3202, REQ-3666: an approved decision with its plan is placed at implement (REQ-0321 for the drafts)."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "Waiting for approval")
        self.assertIn("RES-0002 research, draft", lines[1])
        self.assertIn("next: implement ADR-0001", done.stdout)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        self.assertIn("closed: ADR-0001", repository.run("status").stdout)
    def test_status_places_a_decision_with_no_plan(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "\n## Plan\n\nText.\n", "\n")
        self.assertIn("waiting: ADR-0001 carries no plan", repository.run("status").stdout)
    def test_status_prints_the_same_state_twice(self):
        """REQ-0210: status prints the same text twice, with a decision open or closed."""
        repository = self.repo()
        first = repository.run("status").stdout
        self.assertIn("next: implement ADR-0001", first)
        self.assertEqual(first, repository.run("status").stdout)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        first = repository.run("status").stdout
        self.assertIn("closed: ADR-0001", first)
        self.assertEqual(first, repository.run("status").stdout)
    def test_the_profile_template_names_no_language(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("template", "profile")
        self.assertEqual(done.returncode, 0, done.stderr)
        path = Path(done.stdout.strip())
        self.assertEqual(path.name, "profile.toml")
        text = path.read_text(encoding="utf-8")
        for section in ("[stages]", "[commits]", "[git]", "[record]", "[prose]"):
            self.assertIn(section, text)
        for word in ("python", "rust", "cargo", "npm", "node", "make", "mise", "gradle", "maven", "go ", "java", ".py", ".rs", ".js"):
            self.assertNotIn(word, text.lower(), word)

    def test_template_prefers_the_repository_own(self):
        repository = self.repo()
        done = repository.run("template", "adr")
        self.assertEqual(Path(done.stdout.strip()), (UNIT / "templates" / "adr.md").resolve())
        own = repository.path / ".meowpaw" / "templates" / "adr.md"
        own.parent.mkdir(parents=True)
        own.write_text("# mine\n", encoding="utf-8")
        done = repository.run("template", "adr")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(Path(done.stdout.strip()).resolve(), own.resolve())
    def test_an_unknown_kind_names_the_kinds(self):
        done = self.repo().run("template", "memo")
        self.assertEqual(done.returncode, 2)
        self.assertIn("research, requirement, adr, spec, bug, insight, vision, constitution", done.stderr)

    def template(self, kind):
        done = self.repo().run("template", kind)
        self.assertEqual(done.returncode, 0, done.stderr)
        return Path(done.stdout.strip()).read_text(encoding="utf-8")

    def test_the_bug_template_names_no_retired_step(self):
        """REQ-3638: the bug template's `enters` comment names no step a draft is refused for."""
        enters = [line for line in self.template("bug").splitlines() if line.startswith("enters:")]
        self.assertEqual(len(enters), 1, enters)
        self.assertNotRegex(enters[0].split("#", 1)[1], r"\b(cover|document|verify)\b")


class RunSkill(unittest.TestCase):
    """SPC-1090 "The driver": `/meow-flow:run` continues past a step with no gate and stops at one (REQ-3202)."""

    def steps(self):
        text = (UNIT / "skills" / "run" / "SKILL.md").read_text(encoding="utf-8")
        block = re.search(r'<steps name="drive the chain">(.*?)</steps>', text, re.S)
        self.assertIsNotNone(block, "the run skill has no drive-the-chain steps")
        items = re.findall(r"^(\d+)\. (.*?)(?=^\d+\. |\Z)", block.group(1), re.S | re.M)
        return {int(number): " ".join(body.split()) for number, body in items}

    def test_the_driver_continues_past_a_step_with_no_gate(self):
        """TSK-2540 criterion 4, REQ-3202: a step reruns `paw status` and continues where no approval gate ends the step."""
        steps = self.steps()
        again = [body for body in steps.values()
                 if re.search(r"\b(without|no) (an )?approval gate", body)
                 and "paw status" in body and "again" in body and "continu" in body]
        self.assertTrue(again, steps)
        self.assertRegex(steps.get(5, ""), r"(?i)\bstop\b.*approval gate")


class Show(unittest.TestCase):
    """SPC-1100: an identifier resolves to its artifact and to what cites it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_show_resolves_an_identifier_and_derives_what_cites_it(self):
        repository = self.repo()
        repository.write("archive/tasks/TSK-0001-a-task.md", archived_task("REQ-0001"))
        done = repository.run("show", "REQ-0001")
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
        self.assertIn("usage: paw show <id>", done.stderr)


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

    def test_a_decision_may_correct_its_plan_until_it_is_done(self):
        """REQ-3676: the plan stays editable while the work corrects it."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Plan\n\nText.", "## Plan\n\n1. The corrected step.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_done_decisions_plan_is_frozen(self):
        """REQ-3676: the plan freezes once the record is done."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                        "commit", "-qam", "done"], cwd=repository.path, check=True, capture_output=True)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Plan\n\nText.", "## Plan\n\n1. A rewritten past.")
        self.assertEqual(self.frozen(repository).returncode, 1)
    def test_a_decision_may_gain_its_projection(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001]\nissue: 7\nprojected: 0123456789ab")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)
    def test_a_decision_may_gain_the_tracker_side_fingerprint(self):
        """TSK-5320, REQ-4704: `tracked` beside `projected` is a mapping field and changes after approval."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001]\nprojected: 0123456789ab\ntracked: fedcba987654")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)
    def test_a_decision_rewritten_outside_its_plan_is_reported(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Decision\n\nText.", "## Decision\n\nSomething else.")
        self.assertEqual(self.frozen(repository).returncode, 1)
    def committed(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        return repository

    def test_an_added_line_citing_a_hash_as_a_revision_is_reported(self):
        repository = self.committed()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Plan\n\nText.", "## Plan\n\nThe fixtures passed at `9f3c2e1`.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("cites the commit 9f3c2e1 as a revision; cite the pull request that carried it", done.stdout)

    def test_an_added_line_citing_a_pull_request_passes(self):
        repository = self.committed()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Plan\n\nText.", "## Plan\n\nThe fixtures passed at the trunk after #12, and a fee was added.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

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

    def test_done_is_a_status_only_frozen_transition(self):
        """TSK-5190 criterion 2, REQ-3678: approved to done with its `pr:` passes, but substantive edits still fail."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001]\npr: 12")
        self.assertEqual(self.frozen(repository).returncode, 0)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Why\n\nText.", "## Why\n\nChanged.")
        self.assertEqual(self.frozen(repository).returncode, 1)


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
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))
        self.assertIn("ADR-0001", repository.run("status").stdout)

    def test_a_repository_with_no_record_prints_nothing(self):
        # An unknown key would make the profile report print, and the session's
        # opening hook must stay silent all the same (SPC-1090).
        repository = Repository(profile='[record]\nroot = "nowhere"\nunread = 1\n')
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("status", "--waiting")
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))
        self.assertIn("nowhere", repository.run("status").stdout)


class Indexes(unittest.TestCase):
    """ADR-1180: a kind's index generated from the tree, and checked for drift."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "---\nid: index\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n"
                         "# Decisions\n\nWritten by hand.\n\n<!-- meow-flow index -->\n<!-- /meow-flow index -->\n")
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

    def test_index_writes_its_table_aligned_as_the_formatter_leaves_it(self):
        """A written index passes the Markdown format check unchanged: each column is padded to its widest cell
        and each separator fills its column, so `paw done` never leaves the gate's fmt-check red."""
        repository = self.repo()
        repository.write("adrs/ADR-0002-a-much-longer-name.md",
                         CLEAN["adrs/ADR-0001-a-choice.md"].replace("ADR-0001", "ADR-0002"))
        repository.run("index", "adr", "--write")
        text = (repository.root / "adrs" / "README.md").read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if line.startswith("|")]
        self.assertEqual(len(rows), 4, text)
        self.assertEqual(len({len(row) for row in rows}), 1, "\n".join(rows))
        for cell in rows[1].strip("|").split("|"):
            self.assertRegex(cell, r"^ -+ $")

    def test_an_index_left_behind_is_reported_and_rewriting_clears_it(self):
        repository = self.repo()
        repository.run("index", "adr", "--write")
        repository.write("adrs/ADR-0002-another.md", CLEAN["adrs/ADR-0001-a-choice.md"].replace("ADR-0001", "ADR-0002"))
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/README.md:12: its generated block is out of date; run paw index decision --write",
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
        repository.edit("adrs/ADR-0001-a-choice.md", "## Why\n\nText.", "## Why\n\nSee REQ-0014.")
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
        repository.edit("bugs/BUG-0001-a-defect.md", "# BUG-0001", "# The gate")
        done = repository.run("find", "approval", "gate")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[1], "ADR-0001 decision, approved: An approval gate for the plan"
                                   " (project/adrs/ADR-0001-a-choice.md, front matter)")
        self.assertEqual(lines[2], "BUG-0001 defect, approved: The gate (project/bugs/BUG-0001-a-defect.md, front matter)")
        self.assertNotIn("Text.", done.stdout)

    def test_find_with_no_match_says_so(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("find", "zebra")
        self.assertEqual(done.returncode, 1)
        self.assertIn("nothing in the record carries zebra", done.stdout)
        self.assertEqual(done.stdout.splitlines()[0], f"exhaustive: read {self.READ} artifacts")

    # Every fixture file but an index is an artifact `find` reads.
    READ = sum(1 for text in CLEAN.values() if "artifact: index" not in text)

    def zebra(self, repository):
        repository.write("requirements/REQ-0201-zebra.md", record(
            "requirement", "REQ-0201", {"topic": "a", "class": "functional", "verification": "static"}, [],
            "\nThe harness MUST stripe the zebra.\n\n## Summary\n\nA zebra, and the zebra again.\n").replace(
                "# REQ-0201", "# Zebra crossing"))

    def test_find_states_its_mode_first_and_its_artifact_count_last(self):
        """TSK-4360 criterion 1, REQ-2590, REQ-2595: the mode line opens the output and the count closes it."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        self.zebra(repository)
        done = repository.run("find", "zebra")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[0], f"exhaustive: read {self.READ + 1} artifacts")
        self.assertEqual(lines[-1], "artifacts matched: 1")

    def test_three_matches_in_one_requirement_count_as_one_artifact(self):
        """TSK-4360 criterion 2, REQ-2595: a word in a title, a statement and a Summary section is one artifact,
        though `find` reads only the first two."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        self.zebra(repository)
        done = repository.run("find", "zebra")
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[-1], "artifacts matched: 1")
        self.assertEqual(len(lines), 3, lines)

    def test_each_hit_ends_with_its_file_and_its_section(self):
        """TSK-4360 criterion 3, REQ-2594: a hit names its file, and the heading or `front matter` it matched in."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        self.zebra(repository)
        repository.edit("research/RES-0002-a-finding.md", "## Summary\n\nText.", "## Summary\n\nZebras cross here.")
        repository.edit("research/RES-0001-synthesis.md", "# RES-0001", "# Zebra synthesis")
        done = repository.run("find", "zebra")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[1:-1], [
            "REQ-0201 requirement, approved: Zebra crossing (project/requirements/REQ-0201-zebra.md, front matter)",
            "RES-0001 research, approved: Zebra synthesis (project/research/RES-0001-synthesis.md, front matter)",
            "RES-0002 research, approved: Zebras cross here. (project/research/RES-0002-a-finding.md, Summary)",
        ])

    def test_twenty_five_matches_print_twenty_hits_and_count_twenty_five(self):
        """TSK-4360 criterion 4, REQ-2595: the limit cuts the hits and never the count."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for n in range(301, 326):
            repository.write(f"requirements/REQ-0{n}-zebra.md", record(
                "requirement", f"REQ-0{n}", {"topic": "a", "class": "functional", "verification": "static"}, [],
                "\nThe harness MUST stripe the zebra.\n"))
        done = repository.run("find", "zebra")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[0], f"exhaustive: read {self.READ + 25} artifacts")
        self.assertEqual(len([line for line in lines if line.startswith("REQ-0")]), 20, lines)
        self.assertEqual(len(lines), 22, lines)
        self.assertEqual(lines[-1], "artifacts matched: 25")

    def test_rule_m7_says_what_each_search_supports(self):
        """TSK-4360 criterion 5, REQ-2592, REQ-2594, REQ-2596, REQ-2597: M7 limits an absence to an exhaustive
        search, reads a hit before quoting it, and treats an index as a local cache."""
        text = (UNIT / "skills" / "method" / "SKILL.md").read_text(encoding="utf-8")
        rule = re.search(r"^- M7\.\s(.*?)(?=^- M8\.\s)", text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(rule)
        m7 = re.sub(r"\s+", " ", rule.group(1))
        self.assertRegex(m7, r"has no X only from a search whose first line says `exhaustive`")  # REQ-2592
        self.assertRegex(m7, r"from a `ranked` one only that the search found X")  # REQ-2592
        self.assertRegex(m7, r"[Rr]ead a hit with `paw show` before you quote it")  # REQ-2594
        self.assertRegex(m7, r"refresh the index before you rely on a miss")  # REQ-2596
        self.assertRegex(m7, r"resolve each hit to its file before you cite it")  # REQ-2596
        self.assertRegex(m7, r"report the result as local to this machine")  # REQ-2597

    def test_find_needs_a_word(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("find")
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage: paw find", done.stderr)


class ReadingEnvironment(unittest.TestCase):
    """ADR-1320: every read of source control has prompting, paging, advice and machine-wide configuration off."""

    def test_each_read_of_git_runs_in_the_reading_environment(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        real = shutil.which("git")
        stand_in = repository.path.parent / "bin"
        stand_in.mkdir()
        log = repository.path.parent / "git.log"
        (stand_in / "git").write_text(
            "#!/bin/sh\n"
            f"printf '%s %s %s %s %s\\n' \"$GIT_TERMINAL_PROMPT\" \"$GIT_PAGER\" \"$GIT_ADVICE\" \"$GIT_CONFIG_NOSYSTEM\" \"$1\" >> {log}\n"
            f"exec {real} \"$@\"\n", encoding="utf-8")
        (stand_in / "git").chmod(0o755)
        env = {**os.environ, "PATH": f"{stand_in}:{os.environ['PATH']}"}
        for command in (["status"], ["check", "frozen"], ["check", "coverage"]):
            subprocess.run([str(BIN), *command], cwd=repository.path, capture_output=True, text=True, env=env)
        calls = log.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(calls), 3, calls)
        for call in calls:
            self.assertEqual(call.split()[:4], ["0", "cat", "0", "1"], call)


class ReadOnly(unittest.TestCase):
    """ADR-1200: the commands that read the record write nothing, and repeat themselves."""

    COMMANDS = (["check"], ["check", "frozen"], ["status"], ["status", "--waiting"], ["ready", "design", "REQ-0001"],
                ["template", "adr"], ["show", "REQ-0001"], ["index", "requirement"], ["new", "adr"],
                ["find", "task"], ["count"])

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
        repository.write("adrs/README.md", "# Decisions\n\n<!-- meow-flow index -->\n<!-- /meow-flow index -->\n")
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(sorted(p.name for p in (repository.root / "adrs").iterdir()),
                         ["ADR-0001-a-choice.md", "README.md"])
        written = (repository.root / "adrs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("| [ADR-0001](ADR-0001-a-choice.md) |", written)
        self.assertIn("<!-- /meow-flow index -->", written)

    def test_an_index_with_the_old_markers_is_no_longer_read(self):
        """REQ-3190, ADR-1390: from 0.32.0 the markers before the rename are not read, and writing names the new ones."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "# Decisions\n\n<!-- meow-method index -->\n<!-- /meow-method index -->\n")
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("has no <!-- meow-flow index --> block to write into", done.stdout)


class Where(unittest.TestCase):
    def test_a_root_outside_the_repository_is_read_there(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        elsewhere = Path(outside.name) / "record"
        repository = Repository(profile=f'[record]\nroot = "{elsewhere}"\n', root=str(elsewhere))
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: closed")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(f"{elsewhere.resolve()}/adrs/ADR-0001-a-choice.md:4: status closed is not one a decision stores",
                      done.stdout)
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
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: closed")

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



class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "paw"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "paw").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "check"], cwd=tmp, env={"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"}, capture_output=True, text=True, input="")
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
            self.assertIn("not checked", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("install meow-core", done.stdout)


    def test_a_missing_binary_at_session_start_says_so_and_lets_the_session_begin(self):
        """TSK-4925 criterion 3, SPC-1240 "A hook whose program is missing": the `SessionStart` hook blocks
        nothing, so with no binary it prints that the record wasn't checked and how to install, and exits 0."""
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "paw"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "paw").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "status", "--waiting"], cwd=tmp,
                                  env={"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"},
                                  capture_output=True, text=True, input="")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("not checked", done.stdout)
            self.assertIn("claude plugin install meow-core@meowpaw", done.stdout)


class Named(unittest.TestCase):
    """REQ-3168, REQ-3190, ADR-1390: the unit is meow-flow, and its command is paw."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_every_usage_line_and_message_names_paw(self):
        repository = self.repo()
        done = [repository.run(*args) for args in
                [("check",), ("show",), ("ready",), ("find",), ("count", "x"), ("check", "nothing"), ("show", "REQ-0999")]]
        self.assertEqual(done[0].returncode, 0, done[0].stdout + done[0].stderr)
        said = "".join(run.stdout + run.stderr for run in done)
        self.assertIn("usage: paw show <id>", said)
        self.assertIn("paw check: no check is named nothing", said)
        self.assertIn("paw show: REQ-0999 resolves to nothing", said)
        self.assertNotIn("meow-method", said)

    def test_the_unit_is_named_meow_flow(self):
        manifest = json.loads((UNIT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "meow-flow")
        self.assertEqual(UNIT.name, "meow-flow")
        self.assertEqual(sorted(p.name for p in (UNIT / "bin").iterdir() if p.is_file()), ["paw"])

    def test_nothing_the_unit_ships_names_the_old_unit(self):
        found = [f"{path.relative_to(UNIT)}:{number}"
                 for path in sorted(UNIT.rglob("*"))
                 if path.is_file() and path.suffix in {".md", ".json", ".toml", ""} and "tests" not in path.parts
                 and path.parent.parent != UNIT / "bin"
                 for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
                 if "meow-method" in line]
        self.assertEqual(found, [])



class DefectIsItsOwnWork(unittest.TestCase):
    """ADR-3090: a defect authorises its own work, with its plan, on the same level as a decision."""

    SECTIONS = ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"]

    def repo(self, status="approved", plan=True):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("bugs/BUG-0002-a-second-defect.md", record(
            "bug", "BUG-0002", {"status": status, "violates": "REQ-0001", "severity": "minor",
                                "found": "2026-01-01", "enters": "implement"},
            self.SECTIONS + (["Plan"] if plan else [])))
        return repository

    def test_an_approved_defect_with_a_plan_is_ready(self):
        """REQ-0352, REQ-3674: a defect record authorises work exactly as a decision record does."""
        repository = self.repo()
        done = repository.run("ready", "implement", "BUG-0002")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("next: implement BUG-0002", repository.run("status").stdout)

    def test_a_draft_defect_is_not_ready(self):
        """REQ-0352: a draft defect authorises nothing yet."""
        done = self.repo(status="draft").run("ready", "implement", "BUG-0002")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("BUG-0002, a defect, is draft and not approved", done.stdout)

    def test_a_defect_entering_at_implement_with_no_plan_is_refused(self):
        """REQ-3674: `ready`, `status` and the draft rule agree that it holds its plan."""
        repository = self.repo(plan=False)
        done = repository.run("ready", "implement", "BUG-0002")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("BUG-0002 carries no plan", done.stdout)
        self.assertIn("waiting: BUG-0002 carries no plan", repository.run("status").stdout)
        self.assertIn("enters at implement and carries no ## Plan (REQ-3674)",
                      self.repo(status="draft", plan=False).run("check", "rules").stdout)

    def test_a_defects_plan_and_closed_by_change_after_approval(self):
        """REQ-3676: an approved defect's plan and Closed by change, and its diagnosis doesn't."""
        repository = self.repo()
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        repository.edit("bugs/BUG-0002-a-second-defect.md", "## Plan\n\nText.", "## Plan\n\n1. The corrected step.")
        repository.edit("bugs/BUG-0002-a-second-defect.md", "## Closed by\n\nText.", "## Closed by\n\nThe reproduction, now a check.")
        done = repository.run("check", "frozen")
        self.assertEqual(done.returncode, 0, done.stdout)
        repository.edit("bugs/BUG-0002-a-second-defect.md", "## Triage\n\nText.", "## Triage\n\nRewritten.")
        self.assertEqual(repository.run("check", "frozen").returncode, 1)


class Triage(unittest.TestCase):
    """ADR-1440: a defect's triage, reproduction and closing, held by paw check."""

    SECTIONS = ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"]

    def check(self, fields, edits=(), extra=None):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        base = {"severity": "minor", "found": "2026-01-01"}
        base.update(fields)
        repository.write("bugs/BUG-0003-a-report.md", record("bug", "BUG-0003", base, self.SECTIONS))
        for old, new in edits:
            repository.edit("bugs/BUG-0003-a-report.md", old, new)
        if extra:
            extra(repository)
        return repository.run("check", "rules").stdout

    def test_a_triaged_draft_names_where_it_enters(self):
        """REQ-0360: the triage answer decides which step the defect enters at."""
        said = self.check({"status": "draft", "violates": "REQ-0001"})
        self.assertIn("has a Triage section and no enters", said)

    def test_entering_at_implement_needs_a_violated_requirement(self):
        """REQ-0358: triage first answers whether a requirement in force covers the behaviour."""
        said = self.check({"enters": "implement"})
        self.assertIn("enters implement and names no requirement it violates", said)

    def test_a_defect_may_enter_at_cover(self):
        """TSK-2530 criterion 10, REQ-3207: `enters: cover` is a step, and naming what it violates is enough."""
        said = self.check({"enters": "cover", "violates": "REQ-0001"})
        self.assertNotIn("enters", said)
        self.assertIn("rules: 0 findings", said)

    def test_a_defect_entering_at_cover_names_what_it_violates(self):
        """TSK-2530 criterion 10, REQ-3207: a defect entering at cover names the requirement it violates."""
        said = self.check({"enters": "cover"})
        self.assertIn("enters cover and names no requirement it violates", said)
        self.assertNotIn("which is not a step", said)

    def test_a_triaged_defect_carries_a_reproduction(self):
        """REQ-0364: a defect carries a reproduction before it is triaged."""
        said = self.check({"enters": "requirements"}, [("## Reproduction\n\nText.", "## Reproduction\n")])
        self.assertIn("is triaged with an empty Reproduction", said)

    def test_a_rejected_report_records_why(self):
        """REQ-0370: a defect closed as not a defect records the reasoning."""
        said = self.check({"status": "rejected"}, [("## Triage\n\nText.", "## Triage\n")])
        self.assertIn("is rejected as no defect with an empty Triage", said)

    def test_a_closed_defect_names_its_regression_check(self):
        """REQ-0368: the check that closes a defect remains as a regression check."""
        said = self.check({"status": "done", "violates": "REQ-0001"}, [("## Closed by\n\nText.", "## Closed by\n")])
        self.assertIn("is done with an empty Closed by", said)
        said = self.check({"status": "done", "violates": "REQ-0001"})
        self.assertNotIn("Closed by", said)
    def test_severity_is_required(self):
        """REQ-0372: severity is recorded on the defect."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("bugs/BUG-0003-a-report.md", record("bug", "BUG-0003", {"found": "2026-01-01"}, self.SECTIONS))
        said = repository.run("check", "front-matter").stdout
        self.assertIn("BUG-0003-a-report.md", said)
        self.assertIn("severity", said)

    def test_prompted_by_names_a_defect(self):
        """REQ-0362: a record a defect prompted cites the defect."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("requirements/REQ-0001-an-obligation.md", "topic: a", "topic: a\nprompted-by: ADR-0001")
        said = repository.run("check", "rules").stdout
        self.assertIn("is prompted by ADR-0001, which is not a defect", said)


class Connections(unittest.TestCase):
    """ADR-1470: each chain is checked to its research, and each citation against its target's date."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_an_evaluation_case_may_name_a_record_that_does_not_exist(self):
        """ADR-1490: an evaluation case's sample record is fixture material, not a document citing the record."""
        repository = self.repo()
        case = repository.path / "plugins" / "unit" / "evals" / "a-case" / "prompt.md"
        case.parent.mkdir(parents=True)
        case.write_text("Review this record.\n\n---\nid: REQ-0999\n---\n\nREQ-0999 MUST hold.\n", encoding="utf-8")
        done = repository.run("check", "identifiers")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_an_approved_decision_over_draft_research_names_the_chain(self):
        """REQ-0139: a decision whose own links resolve is reported where the research under it is a draft."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/adrs/ADR-0001-a-choice.md: rests on RES-0002, a draft, through "
                      "ADR-0001 -> REQ-0001 -> RES-0002", done.stdout)
    def test_a_draft_over_a_withdrawn_requirement_is_reported(self):
        """REQ-0139: a draft still being written can be moved off a withdrawn provider."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/adrs/ADR-0001-a-choice.md: rests on REQ-0001, which is withdrawn, through "
                      "ADR-0001 -> REQ-0001", done.stdout)

    def test_a_living_artifact_over_a_rejected_provider_is_reported(self):
        """REQ-0139: a living artifact can be moved off a rejected provider, so check reports it."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: rejected")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/specs/SPC-0001-a-part.md: rests on RES-0002, which is rejected, through "
                      "SPC-0001 -> REQ-0001 -> RES-0002", done.stdout)
        self.assertNotIn("project/adrs/ADR-0001-a-choice.md: rests on", done.stdout)

    def test_a_draft_citing_a_later_revision_is_suspect(self):
        """REQ-0141: a draft citing an artifact revised after it is reported, and so is a living one."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-01")
        done = repository.run("check", "relations")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/adrs/ADR-0001-a-choice.md:6: addresses REQ-0001, revised 2026-02-01, "
                      "after this record's 2026-01-01, so the citation is suspect", done.stdout)
        self.assertIn("project/specs/SPC-0001-a-part.md:6: states REQ-0001, revised 2026-02-01", done.stdout)
        # With the provider a draft, the requirement's provider rule also fires
        # (REQ-3900), so the count is three.
        self.assertIn("project/requirements/REQ-0001-an-obligation.md: REQ-0001 is in force and names no "
                      "approved decision that addresses or postpones it (REQ-3900)", done.stdout)
        self.assertIn("relations: 3 findings", done.stdout)

    def test_an_approved_record_citing_a_later_revision_is_marked_by_show(self):
        """REQ-0141: a frozen record can't be revised, so show marks its suspect citation and check passes."""
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-01")
        repository.edit("specs/SPC-0001-a-part.md", "revised: 2026-01-01", "revised: 2026-03-01")
        done = repository.run("check", "relations")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        shown = repository.run("show", "ADR-0001").stdout
        self.assertIn("  addresses: REQ-0001 (suspect: revised 2026-02-01, after this record)", shown)

    def test_a_kinds_index_revised_later_is_never_a_suspect_citation(self):
        """A kind's index is rewritten as its kind grows, so a record citing it is never suspect by its date."""
        repository = self.repo()
        repository.edit("research/RES-0001-synthesis.md", "revised: 2026-01-01", "revised: 2026-02-01")
        self.assertNotIn("suspect", repository.run("show", "RES-0002").stdout)
        self.assertNotIn("RES-0002 elaborates RES-0001", repository.run("status").stdout)



class Reported(unittest.TestCase):
    """ADR-1470: status reports what only a new record can fix, and fails on none of it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_an_approved_unconnected_artifact_is_listed_and_a_draft_is_not(self):
        """REQ-0143: an artifact nothing cites and that cites nothing is reported, once it is approved."""
        repository = self.repo()
        sections = ["Summary", "Method", "Conclusions", "Sources"]
        repository.write("research/RES-0003-alone.md", record("research", "RES-0003", {}, sections))
        repository.write("research/RES-0004-being-written.md", record("research", "RES-0004", {"status": "draft"}, sections))
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("  unconnected, citing nothing and cited by nothing: RES-0003\n", done.stdout)

    def test_a_rejected_provider_and_a_frozen_suspect_citation_are_reported(self):
        """REQ-0143: what only a new record can fix is reported by status and fails nothing."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: rejected")
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-01")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("  RES-0002, rejected, under 2 approved artifacts: ADR-0001, REQ-0001\n", done.stdout)
        self.assertIn("  2 suspect citations in approved artifacts: ADR-0001 addresses REQ-0001, BUG-0001 violates "
                      "REQ-0001\n", done.stdout)

    def test_the_share_resting_on_judgement_is_stated(self):
        """REQ-0161: the requirements in force are counted by how they are verified."""
        repository = self.repo()
        for number, verification in ((2, "behavioural"), (3, "evaluation"), (4, "judgement\nverifier: agent"),
                                     (5, "judgement\nverifier: person")):
            repository.write(f"requirements/REQ-000{number}-more.md", record(
                "requirement", f"REQ-000{number}",
                {"topic": "a", "class": "functional", "verification": verification, "elaborates": "RES-0002"}, []))
        said = repository.run("status").stdout
        self.assertIn("  by verification: 1 static, 1 behavioural, 1 evaluation, 2 judgement "
                      "(1 by an agent, 1 by a person)\n", said)
        self.assertIn("  3 of 5 rest on evaluation or judgement, not on a mechanical check\n", said)


class VerificationKind(unittest.TestCase):
    """ADR-1510: every requirement declares one of the four kinds of check."""

    def test_a_kind_outside_the_four_is_reported_on_drafts_and_approved_records(self):
        """REQ-1664: a requirement's kind of check is one the harness knows."""
        for status in ("draft", "approved"):
            repository = Repository()
            self.addCleanup(repository.tmp.cleanup)
            repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", f"status: {status}")
            repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", "verification: statc")
            done = repository.run("check", "rules")
            self.assertEqual(done.returncode, 1, status + done.stdout + done.stderr)
            self.assertIn("verification statc is not one of static, behavioural, evaluation and judgement", done.stdout)

    def test_each_of_the_four_passes(self):
        """REQ-1664: the four kinds are the whole vocabulary."""
        for kind in ("static", "behavioural", "evaluation"):
            repository = Repository()
            self.addCleanup(repository.tmp.cleanup)
            repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", f"verification: {kind}")
            done = repository.run("check", "rules")
            self.assertEqual(done.returncode, 0, kind + done.stdout + done.stderr)
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", "verification: judgement\nverifier: agent")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 0, "judgement" + done.stdout + done.stderr)


STEPS = ("research", "requirements", "design", "spec", "implement", "review")
METHOD = UNIT / "skills" / "method"
REPOSITORY = UNIT.parent.parent

# Where each step's artifact lands, as a path pattern under the record root the profile resolves (REQ-3203,
# BUG-1264). Review is read apart: a page isn't under the record root, and review writes nothing.
LANDS = {
    "research": ["research/res-nnnn-<topic>.md"],
    "requirements": ["requirements/req-nnnn-<slug>.md"],
    "design": ["adrs/adr-nnnn-<slug>.md"],
    "spec": ["specs/spc-nnnn-<topic>.md"],
    "implement": ["the test files", "user-facing page", "the record itself"],
}
RECORD_ROOT = ("[record] root", ".meowpaw/profile.toml", "project/")


def flat(text):
    """Lower case, no backticks or heading marks, and every run of white space one space, so a wrapped line
    reads as one and a section named as `## Cover` reads as its name."""
    return re.sub(r"\s+", " ", re.sub(r"#+\s*", "", text.replace("`", ""))).lower().strip()


OUTCOMES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED")


def word_in(word, text):
    """Whether `text` names the outcome `word` as a whole word, so DONE_WITH_CONCERNS doesn't name DONE."""
    return re.search(rf"(?<![A-Za-z_]){word}(?![A-Za-z_])", text) is not None


def outcomes_named(text):
    return {w for w in OUTCOMES if word_in(w, text)}


def sentences(text):
    """Each sentence of a prompt, with a list item and a table row each ending one, white space made single and
    backticks dropped, so a rule is read clause by clause whether it is prose, a list or a table."""
    out = []
    for part in re.split(r"\n(?=\s*(?:[-|*]|\d+\.)\s)|\n\s*\n", text):
        part = re.sub(r"\s+", " ", part.replace("`", "")).strip()
        out.extend(s for s in re.split(r"(?<=[.;])\s+", part) if s)
    return out


def together(text, word, pattern):
    """Whether one sentence of `text` names the outcome `word` and matches `pattern`, ignoring case."""
    return any(word_in(word, s) and re.search(pattern, s, re.IGNORECASE) for s in sentences(text))


def tagged(text, tag):
    found = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.DOTALL)
    return found.group(1) if found else ""


class Grouping(unittest.TestCase):
    """ADR-1800 and SPC-1070 "The layout": the defect kind forbids every grouping field, so a defect is one
    issue and sits under no other record."""

    BUG = "bugs/BUG-0001-a-defect.md"
    GROUPINGS = ("milestone", "parent", "project", "sprint", "iteration", "label", "labels")

    def test_every_grouping_field_is_reported_on_a_defect(self):
        """TSK-2930 criterion 1, BUG-1301: each field ADR-1800 forbids is reported by file, line and field, so a
        layout that drops one field fails here. Line 7 is the first line after the fixture's own fields."""
        for field in self.GROUPINGS:
            with self.subTest(field=field):
                repository = Repository()
                self.addCleanup(repository.tmp.cleanup)
                repository.edit(self.BUG, "violates: REQ-0001", f"violates: REQ-0001\n{field}: x")
                done = repository.run("check")
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertIn(f"project/{self.BUG}:7: carries {field},", done.stdout)


class MethodSkill(unittest.TestCase):
    """ADR-2300: the method's prompts name six steps (REQ-3666) and where each step's artifact lands (REQ-3203)."""

    def step(self, name):
        path = METHOD / "steps" / f"{name}.md"
        self.assertTrue(path.is_file(), f"{path} doesn't exist")
        return path.read_text(encoding="utf-8")

    def assertInOrder(self, text, where):
        """The ten names appear as one list in order: `a, b, ... and z`, the last comma optional."""
        pattern = r",\s+".join(STEPS[:-1]) + r",?\s+and\s+" + STEPS[-1]
        self.assertRegex(re.sub(r"\s+", " ", text), pattern, where)

    def test_each_role_names_where_its_artifact_lands(self):
        """REQ-3203: each role names its path pattern under the record root, implement its tests, pages and
        the record, and review nothing."""
        for name, patterns in LANDS.items():
            role = flat(tagged(self.step(name), "role"))
            for phrase in RECORD_ROOT + tuple(patterns):
                with self.subTest(step=name, phrase=phrase):
                    self.assertIn(phrase, role)
        self.assertIn("writes no finding into the record", flat(tagged(self.step("review"), "role")))

    def chain(self, text):
        block = next(b for b in re.findall(r"```text\n(.*?)```", text, re.DOTALL) if "research ->" in b)
        return tuple(name.strip() for name in block.split("->")), text.split(block, 1)[0]

    def test_the_living_documents_name_the_chain(self):
        """REQ-3666: the chain in CLAUDE.md's own_method_first and in the vision is the six steps, and the
        vision says six."""
        constitution = (REPOSITORY / "CLAUDE.md").read_text(encoding="utf-8")
        principle = tagged(constitution, "principle")
        self.assertIn("own_method_first", constitution.split(principle, 1)[0][-80:])
        self.assertEqual(self.chain(principle)[0], STEPS)
        vision = (REPOSITORY / "project" / "vision.md").read_text(encoding="utf-8")
        self.assertEqual(self.chain(vision)[0], STEPS)
        self.assertNotRegex(vision.lower(), r"\b(seven|nine|ten) steps\b")
        self.assertRegex(flat(vision), r"\bsix steps\b")


AGENTS = UNIT / "agents"


class RequirementState(unittest.TestCase):
    """REQ-3680, ADR-3090: a requirement's state comes from the decisions, archived tasks and defects that name it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def finish(self, repository):
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")

    def second_requirement(self, repository, addressed=True):
        text = (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8")
        repository.write("requirements/REQ-0002-another.md", text.replace("REQ-0001", "REQ-0002"))
        if addressed:
            repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001, REQ-0002]")
            repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: [REQ-0001, REQ-0002]")

    def test_a_requirement_whose_decision_is_done_is_closed(self):
        """REQ-3680, REQ-3602: a done decision closes it, and nothing says verified."""
        repository = self.repo()
        self.finish(repository)
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("State\n  closed\n  ADR-0001 done\n", done.stdout)
        self.assertNotIn("verified", done.stdout)

    def test_a_done_archived_task_closes_a_requirement(self):
        """REQ-3680: closure from before the upgrade stays true."""
        repository = self.repo()
        self.second_requirement(repository, addressed=False)
        repository.write("archive/tasks/TSK-0001-a-task.md", archived_task("REQ-0002"))
        self.assertIn("State\n  closed\n  TSK-0001 done\n", repository.run("show", "REQ-0002").stdout)

    def test_a_decision_still_in_work_keeps_a_requirement_open(self):
        """REQ-3680: a done decision closes nothing while another approved decision still addresses it."""
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        repository.write("adrs/ADR-0002-a-second.md", decision.replace("ADR-0001", "ADR-0002"))
        self.finish(repository)
        self.assertIn("State\n  open, in a decision not yet done\n", repository.run("show", "REQ-0001").stdout)
        repository.edit("adrs/ADR-0002-a-second.md", "status: approved", "status: done")
        self.assertIn("State\n  closed\n", repository.run("show", "REQ-0001").stdout)

    def test_a_requirement_no_decision_names_is_open(self):
        """REQ-3680: nothing naming it leaves it open, never closed."""
        repository = self.repo()
        self.second_requirement(repository, addressed=False)
        self.assertIn("State\n  open, named by no decision\n", repository.run("show", "REQ-0002").stdout)

    def test_an_open_defect_reopens_a_closed_requirement(self):
        """REQ-3610: an open defect naming the requirement in violates reopens it, draft or approved."""
        repository = self.repo()
        self.finish(repository)
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: draft")
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)

    def test_a_defect_stored_done_closes_the_requirement_again(self):
        """REQ-3678, REQ-3610: a defect closes by storing `done`, whatever its Closed by says."""
        repository = self.repo()
        self.finish(repository)
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        self.assertIn("State\n  closed\n", repository.run("show", "REQ-0001").stdout)

    def test_a_decision_may_address_several_requirements(self):
        """REQ-3668: one decision naming three requirements is no coverage finding."""
        repository = self.repo()
        self.second_requirement(repository)
        text = (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8")
        repository.write("requirements/REQ-0003-a-third.md", text.replace("REQ-0001", "REQ-0003"))
        repository.edit("adrs/ADR-0001-a-choice.md", "REQ-0001, REQ-0002]", "REQ-0001, REQ-0002, REQ-0003]")
        repository.edit("specs/SPC-0001-a-part.md", "REQ-0001, REQ-0002]", "REQ-0001, REQ-0002, REQ-0003]")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("coverage: 3 of 3 requirements in force land in a record\n", done.stdout)

    def test_status_counts_requirements_by_their_state(self):
        """REQ-3680, REQ-3602: the counts name closed and open, and no verified state."""
        repository = self.repo()
        self.finish(repository)
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        self.second_requirement(repository, addressed=False)
        self.assertIn("Requirements\n  2 in force: 1 closed, 0 in a decision not yet done, 0 reopened by a defect, "
                      "0 postponed, 1 named by no decision\n", repository.run("status").stdout)

    def test_status_closes_a_done_decision(self):
        """REQ-3678: a done decision is closed, and no document or verify step is named."""
        repository = self.repo()
        self.finish(repository)
        status = repository.run("status").stdout
        self.assertIn("closed: ADR-0001", status)
        self.assertNotIn("verify", status)
        self.assertNotIn("document", status)

    def postpone(self, repository, reverse):
        self.second_requirement(repository, addressed=False)
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        decision = decision.replace("ADR-0001", "ADR-0002").replace("addresses: [REQ-0001]", "addresses: []\npostpones: [REQ-0002]")
        repository.write("adrs/ADR-0002-not-now.md", decision.replace("## What would reverse it\n\nText.", f"## What would reverse it\n\n{reverse}"))

    def test_status_lists_each_postponement_with_its_condition(self):
        """REQ-3622: status lists each postponed requirement with the first entry of the decision's What would reverse it."""
        repository = self.repo()
        self.postpone(repository, "- A second repository\n  asks for it.\n- The owner asks.")
        self.assertIn("Postponed\n  REQ-0002 by ADR-0002, until: A second repository asks for it.\n\n",
                      repository.run("status").stdout)

    def test_brief_status_keeps_what_moves_and_counts_the_rest(self):
        """`--brief` keeps the drafts, each open decision and the requirement counts, and counts closed decisions,
        postponements and frozen findings, because a session reads it and the full list costs its context."""
        repository = self.repo()
        self.postpone(repository, "- A second repository asks for it.")
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        open_status = repository.run("status", "--brief")
        self.assertEqual(open_status.returncode, 0, open_status.stderr)
        self.assertIn("RES-0002 research, draft", open_status.stdout)
        self.assertIn("  ADR-0001 ", open_status.stdout)
        self.assertIn("Requirements\n  2 in force:", open_status.stdout)
        self.assertIn("Postponed\n  1 requirement, listed by `paw status`\n", open_status.stdout)
        self.assertNotIn("until:", open_status.stdout)
        self.finish(repository)
        self.assertIn("closed: ADR-0001", repository.run("status").stdout)
        closed = repository.run("status", "--brief").stdout
        self.assertNotIn("closed: ADR-0001", closed)
        self.assertIn("1 closed, listed by `paw status`", closed)
        self.assertIn("Only a new record can fix\n", closed)

    def test_a_numbered_condition_is_read_to_its_first_item(self):
        """REQ-3622: a numbered list with no blank lines is read to its first item."""
        repository = self.repo()
        self.postpone(repository, "1. A second repository asks.\n2. The owner asks.")
        self.assertIn("  REQ-0002 by ADR-0002, until: A second repository asks.\n\n", repository.run("status").stdout)

    def test_a_postponement_whose_later_decision_was_withdrawn_is_listed_and_counted_alike(self):
        """REQ-3622: a requirement whose only later decision is withdrawn is postponed in the count and in the list."""
        repository = self.repo()
        self.postpone(repository, "- The owner asks.")
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        repository.write("adrs/ADR-0003-dropped.md", decision.replace("ADR-0001", "ADR-0003").replace(
            "addresses: [REQ-0001]", "addresses: [REQ-0002]").replace("status: approved", "status: withdrawn"))
        status = repository.run("status").stdout
        self.assertIn("1 postponed", status)
        self.assertIn("  REQ-0002 by ADR-0002, until: The owner asks.\n", status)


SIX_STEPS = "research, requirements, design, spec, implement, review"


class SixSteps(unittest.TestCase):
    """ADR-3090, ADR-2300: `paw` knows six steps, reads no Cover, and implements a decision or a defect."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_retired_step_is_an_unknown_step(self):
        """TSK-4060 criterion 1, REQ-3004, REQ-3666: cover, document, verify and epic are refused as any step
        `paw ready` doesn't know, with exit 2 and the six steps in order and nothing else, so `bogus` gets the
        same line with its own name and no pointer follows any of them."""
        repository = self.repo()
        for step in ("cover", "document", "verify", "epic", "bogus"):
            with self.subTest(step=step):
                done = repository.run("ready", step, "ADR-0001")
                self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
                self.assertEqual(done.stdout, "")
                self.assertEqual(done.stderr, f"paw ready: no step is named {step}; the steps are {SIX_STEPS}\n")

    def test_implement_reads_no_cover(self):
        """REQ-3682: an approved decision with a plan and no Cover section is ready to implement."""
        repository = self.repo()
        self.assertNotIn("## Cover", (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8"))
        done = repository.run("ready", "implement", "ADR-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_ready_accepts_done_as_post_approval(self):
        """TSK-5190 criterion 2, REQ-3678: a done decision remains a ready input."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: done")
        self.assertEqual(repository.run("ready", "implement", "ADR-0001").returncode, 0)

    def test_a_retired_step_is_refused_in_a_draft_defect_only(self):
        """REQ-3666: a draft defect may not enter at a retired step; one approved, superseded or withdrawn keeps it."""
        repository = self.repo()
        for step in ("cover", "document", "verify", "epic"):
            repository.edit("bugs/BUG-0001-a-defect.md", "found:", f"enters: {step}\nfound:")
            for status, code in (("approved", 0), ("superseded", 0), ("withdrawn", 0), ("draft", 1)):
                text = (repository.root / "bugs/BUG-0001-a-defect.md").read_text(encoding="utf-8")
                text = re.sub(r"\nstatus: \w+", f"\nstatus: {status}", text, count=1)
                if status == "withdrawn" and "**Withdrawn by" not in text:
                    text = re.sub(r"(\n# [^\n]*\n)", r"\1\n**Withdrawn by ADR-0001. No replacement.**\n", text, count=1)
                repository.write("bugs/BUG-0001-a-defect.md", text)
                done = repository.run("check", "rules")
                self.assertEqual(done.returncode, code, f"{step} {status}: {done.stdout}")
                if code:
                    self.assertIn(f"enters {step}, which is not a step", done.stdout)
            repository.edit("bugs/BUG-0001-a-defect.md", f"enters: {step}\n", "")


class ShortChainPrompts(unittest.TestCase):
    """ADR-3090, ADR-2300: the prompts and templates ask for the six-step chain."""

    def flat(self, path):
        return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))

    def test_the_skill_names_six_steps_in_order(self):
        """REQ-3666: SKILL.md's description and body name the six steps in order."""
        text = (METHOD / "SKILL.md").read_text(encoding="utf-8")
        front, body = text.split("\n---\n", 1)
        pattern = r",\s+".join(STEPS[:-1]) + r",?\s+and\s+" + STEPS[-1]
        description = next(line for line in front.splitlines() if line.startswith("description:"))
        self.assertRegex(description, pattern)
        self.assertRegex(re.sub(r"\s+", " ", body), pattern)

    def test_each_of_the_six_steps_has_one_file(self):
        """REQ-3666: `steps/` holds one file for each of the six steps and no other."""
        self.assertEqual(sorted(p.stem for p in (METHOD / "steps").glob("*.md")), sorted(STEPS))

    def test_nothing_the_unit_ships_dispatches_a_record_reviewer_or_a_skeptic(self):
        """Criterion 2, REQ-3624: no shipped file names the record reviewer or the skeptic, and the agent is gone."""
        self.assertFalse((UNIT / "agents" / "record-reviewer.md").exists())
        found = [str(path.relative_to(UNIT)) for path in sorted(UNIT.rglob("*"))
                 if path.is_file() and "tests" not in path.parts and "bin" not in path.parts
                 and re.search(r"record-reviewer|skeptic", path.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(found, [])

    def test_implement_writes_the_tests_first(self):
        """REQ-3682: tests in a first commit that fails, not weakened outside a commit saying why, and the
        documentation and `paw done` in the same pull request."""
        text = self.flat(METHOD / "steps" / "implement.md")
        self.assertRegex(text, r"test for each outcome of the plan step a program can check")
        self.assertRegex(text, r"commit of their own, before any commit that implements")
        self.assertRegex(text, r"see each (one|test) fail")
        self.assertRegex(text, r"(modify|weaken).{0,120}commit of its own.{0,60}why")
        self.assertRegex(text, r"documentation.{0,120}same pull request|same pull request.{0,120}documentation")
        self.assertRegex(text, r"paw done <record> --pr <number>")
        self.assertRegex(text, r"Where every stage passed,.{0,400}paw done <record>")
        self.assertRegex(text, r"Where a stage didn't pass, leave the record `approved`")

    def test_review_is_a_code_review_in_the_pull_request(self):
        """REQ-3626, REQ-3612: a review of the change in its pull request, fixed there, written into no
        record, reporting a test that would pass against a wrong implementation."""
        text = self.flat(METHOD / "steps" / "review.md")
        self.assertRegex(text, r"pull request of a decision or a defect")
        self.assertRegex(text, r"fix.{0,80}in (that|the same) pull request")
        self.assertRegex(text, r"Write no finding into the record")
        self.assertRegex(text, r"writes no finding into the record")
        self.assertRegex(text, r"agent with read-only tools")
        self.assertRegex(text, r"fresh agent review the fixes, for at most two rounds")
        self.assertRegex(text, r"End in one verdict")
        self.assertRegex(text, r"would (still )?pass against a wrong implementation")

    def test_the_templates_carry_a_plan_and_the_retired_ones_are_gone(self):
        """REQ-3672, REQ-3674, REQ-3666: the decision and defect templates hold `## Plan`, and no epic or task
        template ships."""
        templates = UNIT / "templates"
        for name in ("adr.md", "bug.md"):
            self.assertIn("## Plan", (templates / name).read_text(encoding="utf-8"), name)
        for name in ("epic.md", "task.md"):
            self.assertFalse((templates / name).exists(), name)

    def test_the_living_documents_name_six_steps(self):
        """REQ-3666: the constitution and the root README give the chain with six steps."""
        root = UNIT.parent.parent
        chain = r"research -> requirements -> design -> spec -> implement -> review"
        for name in ("CLAUDE.md", "README.md", "project/vision.md"):
            text = (root / name).read_text(encoding="utf-8")
            self.assertRegex(text, chain, name)
        for name in ("README.md", "llms.txt", "plugins/meow-flow/README.md"):
            text = re.sub(r"\s+", " ", (root / name).read_text(encoding="utf-8"))
            self.assertNotRegex(text, r"(?i)\b(seven|nine|ten) steps\b", name)
            self.assertRegex(text, r"(?i)\bsix steps\b", name)

    def test_a_criterion_is_decidable_from_its_own_work(self):
        """REQ-3672: the design step asks for a criterion this pull request's own work decides."""
        self.assertRegex(self.flat(METHOD / "steps" / "design.md"), r"this pull request's own work decides")


class MigratedShape(unittest.TestCase):
    """TSK-3860, ADR-2300, REQ-3652: no record carries the old chain's sections or `checked-at`."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def commit(self, repository):
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)

    def test_the_clean_record_carries_no_checked_at(self):
        """A specification and a decision need no `checked-at` to pass every check."""
        repository = self.repo()
        for name in ("specs/SPC-0001-a-part.md", "adrs/ADR-0001-a-choice.md"):
            self.assertNotIn("checked-at", (repository.root / name).read_text(encoding="utf-8"), name)
        self.assertEqual(repository.run("check").returncode, 0)
    def test_checked_at_is_a_retired_field(self):
        """A record still carrying `checked-at` is reported, by file and line."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at: "#1"')
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/ADR-0001-a-choice.md:7: carries checked-at, a retired field", done.stdout)
    def test_a_retired_section_is_reported(self):
        """A record still carrying `## Cover`, `## Verified` or `## Open review findings` is reported by `shape`."""
        for name, section in (("bugs/BUG-0001-a-defect.md", "Cover"), ("requirements/REQ-0001-an-obligation.md", "Verified"),
                              ("adrs/ADR-0001-a-choice.md", "Open review findings")):
            with self.subTest(section=section):
                repository = self.repo()
                path = repository.root / name
                path.write_text(path.read_text(encoding="utf-8") + f"\n## {section}\n\nText.\n", encoding="utf-8")
                done = repository.run("check", "shape")
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertRegex(done.stdout, rf"project/{re.escape(name)}:\d+: carries the section {section}, which is retired")

    def test_a_retired_heading_inside_fenced_code_is_an_example(self):
        """A fenced example showing an old section is text, not a section, whichever fence holds it."""
        repository = self.repo()
        path = repository.root / "adrs/ADR-0001-a-choice.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n```text\n## Cover\n~~~\n## Verified\n```\n\n~~~\n## Cover\n~~~\n",
                        encoding="utf-8")
        self.assertEqual(repository.run("check", "shape").returncode, 0)

    def test_removing_a_retired_section_or_field_leaves_an_approved_record_frozen_and_clean(self):
        """The migration's own edits aren't a change: an approved record loses `## Cover`, `## Open review findings`
        or `checked-at` with no finding, and still can't change anything else."""
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "## Triage", "## Cover\n\n- Checks: none\n\n## Triage")
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001\n", "# REQ-0001\n\n## Open review findings\n\nOne.\n")
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at: "#1"')
        self.commit(repository)
        repository.edit("bugs/BUG-0001-a-defect.md", "## Cover\n\n- Checks: none\n\n## Triage", "## Triage")
        repository.edit("requirements/REQ-0001-an-obligation.md", "\n## Open review findings\n\nOne.\n", "")
        repository.edit("adrs/ADR-0001-a-choice.md", '\nchecked-at: "#1"', "")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout)
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001", "# REQ-0001\n\nIt MUST do more.")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_text_under_a_retired_heading_is_still_a_change(self):
        """A record gaining a retired section, or changing the text of one it carries, is a change like any other."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Consequences", "## Cover\n\nOld.\n\n## Consequences")
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Cover\n\nOld.", "## Cover\n\nA new obligation.")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Cover\n\nA new obligation.", "## Cover\n\nOld.")
        path = repository.root / "requirements/REQ-0001-an-obligation.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n## Verified\n\nIt MUST now do more.\n", encoding="utf-8")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/requirements/REQ-0001-an-obligation.md: approved at HEAD", done.stdout)

    def test_a_retired_heading_with_more_words_is_the_same_section(self):
        """`## Verified, and closed with a criterion unmet` is the Verified section; `## Covered` is not Cover."""
        repository = self.repo()
        path = repository.root / "adrs/ADR-0001-a-choice.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n## Verified, and closed with a criterion unmet\n\nText.\n", encoding="utf-8")
        self.assertIn("carries the section Verified, which is retired", repository.run("check", "shape").stdout)
        path.write_text(text + "\n## Covered\n\nText.\n", encoding="utf-8")
        self.assertNotIn("which is retired", repository.run("check", "shape").stdout)

    def test_a_wrapped_retired_field_and_a_line_opening_with_a_span_are_read(self):
        """A retired field written over several lines is removed whole, and a prose line opening with an inline
        span of backticks isn't a fence, so the section after it is still a section."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at:\n  [\n    "#1",\n  ]')
        repository.edit("bugs/BUG-0001-a-defect.md", "## Triage", "```paw check``` prints nothing.\n\n## Cover\n\nNot yet.\n\n## Triage")
        self.assertIn("carries the section Cover", repository.run("check", "shape").stdout)
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", '\nchecked-at:\n  [\n    "#1",\n  ]', "")
        repository.edit("bugs/BUG-0001-a-defect.md", "## Cover\n\nNot yet.\n\n## Triage", "## Triage")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_blank_line_changed_elsewhere_is_a_change(self):
        """Only the blank lines round a removed section move: one removed inside fenced code is a change."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Consequences", "```text\na\n\n\n\nb\n```\n\n## Consequences")
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "a\n\n\n\nb", "a\n\nb")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_a_record_that_never_carried_one_is_compared_as_it_is(self):
        """The allowances belong to a removal: with nothing retired removed, a changed `revised` or an added blank
        line in an approved record is a change."""
        repository = self.repo()
        self.commit(repository)
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-02")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_one_retired_section_removed_while_another_stays(self):
        """A migration in two steps passes: removing `## Cover` while `## Verified` stays as it was, and removing a
        `checked-at` written as a block list."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Consequences", "## Cover\n\nOld.\n\n## Verified\n\nKept.\n\n## Consequences")
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at:\n- "#1"\n- "#2"')
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Cover\n\nOld.\n\n", "")
        repository.edit("adrs/ADR-0001-a-choice.md", '\nchecked-at:\n- "#1"\n- "#2"', "")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Verified\n\nKept.", "## Verified\n\nChanged.")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_a_first_level_heading_in_a_plan_ends_nothing(self):
        """Only a `## ` heading bounds a section, so a `# ` line in a decision's plan is part of it."""
        repository = self.repo()
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Plan\n\nText.", "## Plan\n\n# ran\n\noutput")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 0)
    def test_a_fence_closes_on_its_own_mark_at_its_own_length(self):
        """A four-mark fence holds a three-mark one, a line with an info string closes nothing, a tilde fence takes
        any info string, and a fence indented four spaces is code, not a fence."""
        for body, reported in (("````markdown\n```text\n## Cover\n```\n## Verified\n````", False),
                               ("```text\n```rust\n## Cover\n```", False),
                               ("~~~ a~b\n## Cover\n~~~", False),
                               ("    ```\n\n## Cover\n\nText.", True)):
            with self.subTest(body=body):
                repository = self.repo()
                path = repository.root / "adrs/ADR-0001-a-choice.md"
                path.write_text(path.read_text(encoding="utf-8") + f"\n{body}\n", encoding="utf-8")
                self.assertEqual("which is retired" in repository.run("check", "shape").stdout, reported)



class ApprovedOnTheBranch(unittest.TestCase):
    """TSK-5290, ADR-3090: a record's approval is read from the working tree, wherever the trunk stands."""

    DECISION = "adrs/ADR-0001-a-choice.md"

    def git(self, repository, *args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
                              cwd=repository.path, check=True, capture_output=True, text=True,
                              env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})

    def repo(self, draft=False):
        """A record whose one open decision is committed on `work` and absent from `main`."""
        repository = Repository(profile='[git]\ntrunk = "main"\n')
        self.addCleanup(repository.tmp.cleanup)
        self.git(repository, "checkout", "-q", "-b", "main")
        decision = (repository.root / self.DECISION).read_text(encoding="utf-8")
        (repository.root / self.DECISION).unlink()
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "base")
        self.git(repository, "checkout", "-q", "-b", "work")
        if draft:
            decision = decision.replace("status: approved", "status: draft")
        (repository.root / self.DECISION).write_text(decision, encoding="utf-8")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "--allow-empty", "-m", "the decision")
        return repository

    def test_a_decision_approved_on_the_branch_is_ready(self):
        """Criterion 1: `ready implement` exits 0 for a decision approved on the branch and absent from the trunk."""
        done = self.repo().run("ready", "implement", "ADR-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_status_names_the_decision_as_next(self):
        """Criterion 2: `status` prints next and no waiting line for that decision."""
        status = self.repo().run("status").stdout
        self.assertIn("next: implement ADR-0001", status)
        self.assertNotIn("waiting: ADR-0001", status)

    def test_a_draft_decision_is_not_ready(self):
        """Criterion 3: reading the working tree still refuses a decision that is a draft there."""
        done = self.repo(draft=True).run("ready", "implement", "ADR-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("ADR-0001", done.stdout)


class OneRecordOnePullRequest(unittest.TestCase):
    """ADR-3090, REQ-3668: the constitution and the method unit state the unit of a pull request."""

    ROOT = Path(__file__).resolve().parents[3]
    FROZEN = ("project/research/", "project/adrs/", "project/archive/", "project/requirements/",
              "project/bugs/", "project/insights/")

    def test_no_living_text_says_a_task_is_a_pull_request(self):
        """REQ-3668: the old statement of the unit appears in no living or shipped file."""
        tracked = subprocess.run(["git", "ls-files"], cwd=self.ROOT, capture_output=True, text=True, check=True)
        found = []
        for name in tracked.stdout.splitlines():
            if name.startswith(self.FROZEN) or "/tests/" in name or name.startswith("project/specs/"):
                continue
            try:
                text = (self.ROOT / name).read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if re.search(r"one task, one branch|task is one pull request|one task one branch", line, re.I):
                    found.append(f"{name}:{number}")
        self.assertEqual(found, [])

    def test_the_constitution_says_a_record_is_one_pull_request(self):
        """REQ-3668: the principle names the decision or the defect as the unit."""
        text = re.sub(r"\s+", " ", (self.ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertRegex(text, r"A decision or a defect is one issue and one pull request")


class ReadDenial(unittest.TestCase):
    """TSK-5065, ADR-2650: the implement step relies on no read denial to keep a file from an agent."""

    ROOT = Path(__file__).resolve().parents[3]

    def test_no_step_relies_on_a_read_denial(self):
        """Criterion 3, REQ-3056: a read denial is a default and never a boundary, in both copies, with its reason."""
        for where in ("plugins", "packages"):
            with self.subTest(copy=where):
                text = " ".join((self.ROOT / where / "meow-flow/skills/method/steps/implement.md")
                                .read_text(encoding="utf-8").split())
                self.assertRegex(text, r"I\d+\. [^.]{0,200}read denial[^.]{0,200}because[^.]{0,200}shell search")


class WriteCommands(unittest.TestCase):
    """TSK-5310, TSK-5311, ADR-2880: a status change that crosses files is one command, and nothing else moves."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def snapshot(self, repository):
        return {str(p.relative_to(repository.root)): p.read_text(encoding="utf-8")
                for p in sorted(repository.root.rglob("*.md"))}

    def changed(self, before, after):
        return sorted(name for name in after if before.get(name) != after[name])

    def lines_changed(self, before, after):
        return [(a, b) for a, b in zip(before.splitlines(), after.splitlines()) if a != b]

    def test_approve_changes_the_status_line_and_nothing_else(self):
        """TSK-5310 criterion 1, REQ-4602: a draft the check accepts is approved, and only its status line moved."""
        repository = self.repo()
        name = "adrs/ADR-0001-a-choice.md"
        repository.edit(name, "status: approved", "status: draft")
        repository.edit(name, "## Plan", "## How I will know it was realised\n\nText.\n\n## What this does not settle\n\nText.\n\n## Plan")
        before = self.snapshot(repository)
        done = repository.run("approve", "ADR-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        after = self.snapshot(repository)
        self.assertEqual(self.changed(before, after), [name])
        self.assertEqual(self.lines_changed(before[name], after[name]), [("status: draft", "status: approved")])
        self.assertEqual(repository.run("check").returncode, 0)
    def test_approve_refuses_a_draft_with_a_finding_and_changes_nothing(self):
        """TSK-5310 criterion 2, REQ-4602: a finding about the draft stops the command, names it, and writes nothing."""
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: draft")
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static\n", "")
        before = self.snapshot(repository)
        done = repository.run("approve", "REQ-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("REQ-0001-an-obligation.md", done.stdout)
        self.assertEqual(self.snapshot(repository), before)

    def test_approve_refuses_a_record_that_is_not_a_draft(self):
        """TSK-5310, REQ-4602: an approved record isn't approved again, and nothing is written."""
        repository = self.repo()
        before = self.snapshot(repository)
        done = repository.run("approve", "ADR-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("not a draft", done.stdout)
        self.assertEqual(self.snapshot(repository), before)

    def test_withdraw_writes_the_tombstone_and_the_status(self):
        """TSK-5310 criterion 3, REQ-4602: the file carries the tombstone naming the replacement and the status."""
        repository = self.repo()
        for ident in ("REQ-0005", "REQ-0007"):
            repository.write(f"requirements/{ident}-another-obligation.md", record(
                "requirement", ident,
                {"topic": "a", "class": "functional", "verification": "static", "elaborates": "RES-0002"}, []))
        repository.write("requirements/README.md", index("index", ["REQ-0001", "REQ-0005", "REQ-0007"]))
        done = repository.run("withdraw", "REQ-0005", "--by", "ADR-0001", "--replaced-by", "REQ-0007")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        text = (repository.root / "requirements/REQ-0005-another-obligation.md").read_text(encoding="utf-8")
        self.assertIn("status: withdrawn", text)
        self.assertIn("**Withdrawn. Replaced by REQ-0007.**", text)
        self.assertIn("ADR-0001", text)
        self.assertEqual(repository.run("check", "front-matter").returncode, 0)

    def test_withdraw_refuses_a_replacement_that_does_not_exist(self):
        """TSK-5310, REQ-4602: a tombstone naming no record is refused, and nothing is written."""
        repository = self.repo()
        before = self.snapshot(repository)
        done = repository.run("withdraw", "REQ-0001", "--by", "ADR-0001", "--replaced-by", "REQ-0099")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.snapshot(repository), before)

    def test_done_stores_done_and_names_the_pull_request(self):
        """REQ-3678: one command stores `done`, adds `pr:` and changes no other record."""
        repository = self.repo()
        before = self.snapshot(repository)
        done = repository.run("done", "ADR-0001", "--pr", "12")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        files = self.snapshot(repository)
        self.assertEqual(self.changed(before, files), ["adrs/ADR-0001-a-choice.md"])
        front = files["adrs/ADR-0001-a-choice.md"].split("\n---\n", 1)[0]
        self.assertIn("status: done", front)
        self.assertIn("pr: 12", front)
        self.assertEqual(repository.run("check").returncode, 0, repository.run("check").stdout)

    def test_done_closes_a_defect_that_names_its_check(self):
        """REQ-3678, REQ-0368: a defect closes the same way, once its Closed by names a check."""
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "## Closed by\n\nText.", "## Closed by\n\nNot yet.")
        before = self.snapshot(repository)
        done = repository.run("done", "BUG-0001", "--pr", "12")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("BUG-0001's Closed by doesn't name the check that closed it", done.stdout)
        self.assertEqual(self.snapshot(repository), before)
        repository.edit("bugs/BUG-0001-a-defect.md", "## Closed by\n\nNot yet.", "## Closed by\n\nThe regression test.")
        done = repository.run("done", "BUG-0001", "--pr", "12")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("status: done", self.snapshot(repository)["bugs/BUG-0001-a-defect.md"])
    def test_done_refuses_what_is_not_an_approved_decision_or_defect(self):
        """REQ-3678, ADR-3090: an archived task, a requirement and a record already done are refused, and nothing moves."""
        repository = self.repo()
        repository.write("archive/tasks/TSK-0001-a-task.md", archived_task("REQ-0001"))
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        before = self.snapshot(repository)
        for ident, said in (("TSK-0001", "only a decision or a defect is closed"),
                            ("REQ-0001", "only a decision or a defect is closed"),
                            ("BUG-0001", "only an approved record is closed")):
            done = repository.run("done", ident, "--pr", "12")
            self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
            self.assertIn(said, done.stdout)
        self.assertEqual(self.snapshot(repository), before)
    def test_done_refuses_a_decision_with_no_plan(self):
        """REQ-3672, REQ-3678: a decision that addresses work closes only with its plan, and nothing moves."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "\n## Plan\n\nText.\n", "\n")
        before = self.snapshot(repository)
        done = repository.run("done", "ADR-0001", "--pr", "12")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("ADR-0001 carries no plan", done.stdout)
        self.assertEqual(self.snapshot(repository), before)


class SynchronisationStep(unittest.TestCase):
    """TSK-5322, REQ-4002: the implement step runs the synchronisation at the start and the end of a record's work."""

    ROOT = Path(__file__).resolve().parents[3]

    def test_the_implement_step_runs_the_synchronisation_at_its_start_and_its_end(self):
        """Criterion 1: where `[tracker] kind` is declared the step names `meow-github sync` twice, in both copies."""
        for where in ("plugins", "packages"):
            with self.subTest(copy=where):
                text = (self.ROOT / where / "meow-flow/skills/method/steps/implement.md").read_text(encoding="utf-8")
                self.assertGreaterEqual(text.count("meow-github sync"), 2, text[-900:])
                self.assertRegex(text, r"(?s)\[tracker\] kind.{0,300}meow-github sync")
                self.assertRegex(text, r"(?is)(before|start).{0,200}meow-github sync|meow-github sync.{0,200}(before|start)")
                self.assertRegex(text, r"(?is)(after|end).{0,200}meow-github sync|meow-github sync.{0,200}(after|end)")

    def test_the_script_the_pack_replaces_is_gone_and_unnamed(self):
        """Criterion 2: `tools/sync_issues.py` doesn't exist, and no living or shipped file names it."""
        self.assertFalse((self.ROOT / "tools" / "sync_issues.py").exists())
        tracked = subprocess.run(["git", "ls-files"], cwd=self.ROOT, capture_output=True, text=True, check=True)
        frozen = ("project/research/", "project/adrs/", "project/archive/", "project/requirements/", "project/bugs/",
                  "project/insights/")
        named = []
        for name in tracked.stdout.splitlines():
            if name.startswith(frozen) or name == "plugins/meow-flow/tests/test_record.py":
                continue
            try:
                if "sync_issues" in (self.ROOT / name).read_text(encoding="utf-8"):
                    named.append(name)
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        self.assertEqual(named, [])


class DeniedDispatch(unittest.TestCase):
    """TSK-2703 criteria 1 and 3, REQ-2978, SPC-1030 "What an agent reports" and SPC-1090 "The review": every
    shipped agent carries the denial rule in the same words, and the review step ends a `BLOCKED` dispatch there."""

    AGENT_FILES = {
        "researcher": AGENTS / "researcher.md",
        "prose": REPOSITORY / "plugins" / "meow-prose" / "agents" / "prose.md",
    }

    def denial_rule(self, name):
        text = self.AGENT_FILES[name].read_text(encoding="utf-8").split("---\n", 2)[2]
        found = [s for s in sentences(text) if re.search(r"\bcall is denied\b", s) and re.search(r"use no other tool to reach the same result", s)]
        self.assertEqual(len(found), 1, f"{name} has {len(found)} sentences stating the denial rule, not one")
        return found[0]

    def test_no_shipped_agent_is_left_out(self):
        """TSK-2703 criterion 1: the agents read here are every agent a unit ships, so a new one is held too."""
        shipped = sorted(str(path.relative_to(REPOSITORY)) for path in (REPOSITORY / "plugins").glob("*/agents/*.md"))
        self.assertEqual(shipped, sorted(str(path.relative_to(REPOSITORY)) for path in self.AGENT_FILES.values()))

    def test_each_agent_carries_the_denial_rule(self):
        """TSK-2703 criterion 1, REQ-2978: where a call is denied, the agent issues no second call in another
        form, reaches the result with no other tool, asks nobody for the permission, ends with BLOCKED naming the
        tool and what it was called on, and the rule states its reason."""
        for name in self.AGENT_FILES:
            with self.subTest(agent=name):
                rule = self.denial_rule(name)
                for pattern, what in (
                    (r"no second call in another form", "no second call in another form"),
                    (r"ask nobody for the permission", "asks nobody"),
                    (r"outcome: BLOCKED", "ends as BLOCKED"),
                    (r"naming the tool and what it was called on", "names the tool and what it was called on"),
                    (r"\bbecause\b", "states its reason"),
                ):
                    self.assertRegex(rule, pattern, what)

    def test_the_agents_carry_one_sentence(self):
        """TSK-2703 criterion 1, REQ-2978, SPC-1030: the denial rule is in the same words in every agent."""
        rules = {name: self.denial_rule(name) for name in self.AGENT_FILES}
        self.assertEqual(len(set(rules.values())), 1, rules)

    def test_the_review_step_ends_a_blocked_dispatch(self):
        """TSK-2703 criterion 3, REQ-2978, SPC-1090 "The review": W13 ends a BLOCKED review with no SendMessage to
        resume it, no second dispatch under the same permissions and no review by the session itself, and reports
        it as not run, never as self-assessed or passed."""
        text = (METHOD / "steps" / "review.md").read_text(encoding="utf-8")
        found = re.search(r"^- W13\.\s(.*?)(?=^- W\d+\.\s|^</rules>|\Z)", text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(found, "the review step has no W13")
        blocked = flat("\n".join(s for s in sentences(found.group(1)) if word_in("BLOCKED", s)))
        for pattern, what in (
            (r"\bno sendmessage to resume\b", "names SendMessage as the resume it refuses"),
            (r"\bno second agent under the same permissions\b", "refuses a second dispatch under the same permissions"),
            (r"\bnever review the change yourself\b", "refuses a review by the session itself"),
            (r"\bnot run\b[^.;]*\bnever as self-assessed or passed\b", "reports it as not run"),
        ):
            with self.subTest(what=what):
                self.assertRegex(blocked, pattern)

    def test_the_steps_brief_the_agent_and_end_a_review_that_did_not_run(self):
        """TSK-2703 criterion 3, REQ-2978: step 2 tells the agent to end a denied call as BLOCKED, since nothing
        else gives it the rule, and step 8 and W8 have an ending for a review that didn't run."""
        text = (METHOD / "steps" / "review.md").read_text(encoding="utf-8")
        steps = flat(tagged(text, "steps"))
        self.assertRegex(steps, r"2\. .*where a tool call is denied it makes no other call for it, asks nobody, and ends with outcome: blocked")
        self.assertRegex(steps, r"8\. .*not run where the first agent reported blocked, the fixes unreviewed where the agent reviewing a round of them did")
        self.assertRegex(flat(text), r"w8\. end in one verdict: finished, not run, or the findings still open")


class ThreatModelPointer(unittest.TestCase):
    """TSK-4380 criterion 4, ADR-2470: design rule D20 sends a decision with a security-relevant boundary to the
    threat model, named by its subject, because the step file ships to repositories that hold none of ours."""

    def rule(self):
        text = (METHOD / "steps" / "design.md").read_text(encoding="utf-8")
        found = re.search(r"^- D20\.\s(.*?)(?=^- D\d+\.\s|^</rules>|\Z)", text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(found, "the design step has no D20")
        return flat(found.group(1))

    def test_d20_updates_the_threat_model_with_its_reason(self):
        """ADR-2470: a decision with a security-relevant boundary updates the threat model the repository's
        specification keeps, and the rule says why."""
        rule = self.rule()
        self.assertRegex(rule, r"\bsecurity-relevant boundary\b")
        self.assertRegex(rule, r"\bupdate the threat model the repository's specification keeps\b")
        self.assertRegex(rule, r"\bthreat model\b[^.]*\bbecause\b")

    def test_d20_names_no_identifier_of_this_repository(self):
        """ADR-2470: the rule names the threat model by its subject, never by a record identifier, a path or a name
        only this repository holds."""
        rule = self.rule()
        self.assertNotRegex(rule, r"\b(?:spc|adr|req|res|epc|tsk|bug|ins)-\d+")
        for name in ("project/", "meowpaw", "paw ", "native tool"):
            self.assertNotIn(name, rule)


if __name__ == "__main__":
    unittest.main()
