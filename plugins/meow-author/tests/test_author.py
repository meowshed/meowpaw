# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every condition `meow-author check` fails on, as SPC-1030 states.

Each fixture builds a scratch repository holding one unit, or a repository's
own `.claude/`, and runs the check. `MEOW_AUTHOR_BIN` names the launcher to
test, so the fixtures can first run against a program that reports nothing
and be seen failing (REQ-2072).
"""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_AUTHOR_BIN", UNIT / "bin" / "meow-author"))
GOOD = """---
name: demo
description: The demo skill. It MUST be loaded before a demo is run.
---

<role>
You run the demo.
</role>

<steps name="demo">
1. Read `${CLAUDE_SKILL_DIR}/notes.md`.
2. Run the demo, report what it printed, and stop.
</steps>

<rules name="demo">
- D1. Run the demo once, because twice changes nothing.
</rules>
"""

NOTES = "<rules name=\"notes\">\n- N1. Note it, because it helps.\n</rules>\n"


class Repository:
    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def check(self, *paths):
        return subprocess.run([str(BIN), "check", *paths], cwd=self.root, capture_output=True, text=True)

    def run_cost(self):
        return subprocess.run([str(BIN), "cost"], cwd=self.root, capture_output=True, text=True)


def unit(skill=GOOD, extra=None):
    files = {"plugins/meow-demo/skills/demo/SKILL.md": skill, "plugins/meow-demo/skills/demo/notes.md": NOTES}
    files.update(extra or {})
    return files


class Check(unittest.TestCase):
    def repo(self, files):
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def fails(self, files, expected, *paths):
        done = self.repo(files).check(*paths)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(expected, done.stdout)

    def test_a_well_formed_unit_passes(self):
        done = self.repo(unit()).check()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 authoring failures", done.stdout)

    def test_a_heading_fails(self):
        """REQ-1112: one structural vocabulary, with no Markdown headings."""
        self.fails(unit(GOOD + "\n## A heading\n"), "a Markdown heading, where the prompt uses tags")

    def test_a_tag_outside_the_vocabulary_fails(self):
        """REQ-1114: the vocabulary is fixed, so a tag outside it is a defect."""
        self.fails(unit(GOOD + "\n<context>\nMore.\n</context>\n"), "<context> is not in the vocabulary SPC-1030 states")

    def test_a_nested_tag_fails(self):
        """REQ-1128: one format across units, so one check audits them all."""
        self.fails(unit(GOOD.replace("<role>\nYou run the demo.", "<role>\n<rules>\n- R1. x.\n</rules>")), "<rules> opens inside <role>")

    def test_a_tag_never_closed_fails(self):
        """REQ-1128: a tag left open is a malformed prompt."""
        self.fails(unit(GOOD.replace("</rules>\n", "")), "<rules> is never closed")

    def test_text_outside_every_tag_fails(self):
        """REQ-1120: every obligation sits inside a tag, where it can be extracted."""
        self.fails(unit(GOOD + "\nAlways run twice.\n"), "text outside every tag")

    def test_a_skill_without_a_description_fails(self):
        """REQ-1110: every unit states what it is for and when to load it."""
        self.fails(unit(GOOD.replace("description: The demo skill. It MUST be loaded before a demo is run.\n", "")), "has no description in its front matter")

    def test_a_commands_directory_fails(self):
        """REQ-1111: one kind of loadable unit, a command being a skill only a person invokes."""
        self.fails(unit(extra={"plugins/meow-demo/commands/go.md": "Go.\n"}), "ships a commands/ directory")

    def test_a_supporting_file_nothing_names_fails(self):
        """REQ-1124, REQ-1142: the core names each supporting file, or nothing loads it."""
        self.fails(unit(extra={"plugins/meow-demo/skills/demo/orphan.md": NOTES}), "orphan.md is never named by the skill's core")

    def test_a_path_without_the_directory_variable_fails(self):
        """REQ-2688: supporting files are addressed through the platform's directory variable."""
        self.fails(unit(GOOD.replace("`${CLAUDE_SKILL_DIR}/notes.md`", "`../demo/notes.md`")), "climbs out of the file with no directory variable")

    def test_a_procedure_without_a_stopping_point_fails(self):
        """REQ-1122: a procedure states where it stops."""
        self.fails(unit(GOOD.replace("report what it printed, and stop.", "and read its output.")), "has a procedure and no step naming where it stops")

    def test_a_repositorys_own_skills_are_checked(self):
        """REQ-1672, REQ-1678: a repository checks its own material with the shipped capability."""
        files = {".claude/skills/local/SKILL.md": GOOD.replace("${CLAUDE_SKILL_DIR}/notes.md", "${CLAUDE_SKILL_DIR}/local-notes.md") + "\n## A heading\n",
                 ".claude/skills/local/local-notes.md": NOTES}
        self.fails(files, ".claude/skills/local/SKILL.md", ".claude")

    def test_nothing_to_check_is_unchecked(self):
        done = self.repo({"README.md": "Nothing here.\n"}).check(".")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unchecked", done.stdout)


AGENT_FIELDS = {
    "maxTurns": "30",
    "tools": "[Read, Grep, Glob]",
    "model": "opus",
    "effort": "high",
    "omitClaudeMd": "false",
    "skills": "[]",
}
SHIPPED_AGENT = "plugins/meow-demo/agents/reviewer.md"
OWN_AGENT = ".claude/agents/local.md"
OUTCOMES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED")
NAMES_ALL_FOUR = "You review the demo and end with outcome: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT or BLOCKED."


def agent(role=NAMES_ALL_FOUR, **changes):
    """An agent declaring the six fields SPC-1030 states, with `changes` applied and a value of None removing a
    field. Its body names the four outcomes unless `role` replaces it, so a field fixture fails on its field alone."""
    fields = dict(AGENT_FIELDS)
    fields.update(changes)
    lines = [f"{name}: {value}" for name, value in fields.items() if value is not None]
    front = "\n".join(["name: reviewer", "description: Reviews the demo and reports findings, editing nothing."] + lines)
    return f"---\n{front}\n---\n\n<role>\n{role}\n</role>\n"


class AgentFields(unittest.TestCase):
    """TSK-2700: an agent declares maxTurns, tools, model, effort, omitClaudeMd and skills, as SPC-1030 states."""

    def repo(self, files):
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def refuses(self, path, text, field, *paths):
        """The check exits 1 with a line naming `path` and `field`."""
        done = self.repo({path: text}).check(*paths)
        self.assertEqual(done.returncode, 1, done.stdout)
        named = [line for line in done.stdout.splitlines() if line.startswith(path) and field in line]
        self.assertTrue(named, f"no failure names {path} and {field}:\n{done.stdout}")
        return done

    def passes(self, path, text, *paths):
        done = self.repo({path: text}).check(*paths)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 authoring failures", done.stdout)

    def test_a_missing_maxTurns_fails(self):
        """TSK-2700 criterion 1, REQ-2974: an agent with no turn ceiling fails, naming maxTurns."""
        self.refuses(SHIPPED_AGENT, agent(maxTurns=None), "maxTurns")

    def test_a_missing_tools_fails(self):
        """TSK-2700 criterion 1, REQ-3270: an agent with no written tools list fails, naming tools."""
        self.refuses(SHIPPED_AGENT, agent(tools=None), "tools")

    def test_a_missing_model_fails(self):
        """TSK-2700 criterion 1, REQ-2988: an agent with no model fails, naming model."""
        self.refuses(SHIPPED_AGENT, agent(model=None), "model")

    def test_a_missing_effort_fails(self):
        """TSK-2700 criterion 1, REQ-2988: an agent with no effort fails, naming effort."""
        self.refuses(SHIPPED_AGENT, agent(effort=None), "effort")

    def test_a_missing_omitClaudeMd_fails(self):
        """TSK-2700 criterion 1, REQ-2982: an agent with no omitClaudeMd fails, naming omitClaudeMd."""
        self.refuses(SHIPPED_AGENT, agent(omitClaudeMd=None), "omitClaudeMd")

    def test_a_missing_skills_fails(self):
        """TSK-2700 criterion 1, REQ-2984: an agent with no skills list fails, naming skills."""
        self.refuses(SHIPPED_AGENT, agent(skills=None), "skills")

    def test_a_zero_ceiling_fails(self):
        """TSK-2700 criterion 2, REQ-2974: maxTurns is a positive integer, so 0 fails."""
        self.refuses(SHIPPED_AGENT, agent(maxTurns="0"), "maxTurns")

    def test_inherit_fails(self):
        """TSK-2700 criterion 2, REQ-2988: inherit leaves the cost to the dispatcher, so it fails."""
        self.refuses(SHIPPED_AGENT, agent(model="inherit"), "model")

    def test_an_unknown_model_alias_fails(self):
        """TSK-2700 criterion 2, REQ-2988: a misspelt alias such as opsu fails."""
        self.refuses(SHIPPED_AGENT, agent(model="opsu"), "model")

    def test_an_unknown_effort_fails(self):
        """TSK-2700 criterion 2, REQ-2988: effort is low, medium, high, xhigh or max, so extreme fails."""
        self.refuses(SHIPPED_AGENT, agent(effort="extreme"), "effort")

    def test_a_wrong_type_fails(self):
        """TSK-2700 criterion 2, REQ-2974, REQ-2988, REQ-2982, REQ-2984: a value of the wrong type fails, naming its field."""
        cases = [
            ("maxTurns", "-1"),
            ("maxTurns", "2.5"),
            ("effort", "3"),
            ("omitClaudeMd", "yes"),
            ("skills", "meow-prose:writing"),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                self.refuses(SHIPPED_AGENT, agent(**{field: value}), field)

    def test_a_shipped_agent_with_every_tool_fails(self):
        """TSK-2700 criterion 3, REQ-3270: a shipped agent with tools "*" can dispatch another agent."""
        self.refuses(SHIPPED_AGENT, agent(tools='"*"'), "tools")

    def test_a_shipped_agent_listing_agent_fails(self):
        """TSK-2700 criterion 3, REQ-3270: a shipped agent listing Agent fails."""
        self.refuses(SHIPPED_AGENT, agent(tools="[Read, Agent]"), "tools")

    def test_a_shipped_agent_listing_task_fails(self):
        """TSK-2700 criterion 3, REQ-3270: a shipped agent listing Task, the older name, fails."""
        self.refuses(SHIPPED_AGENT, agent(tools="[Read, Task]"), "tools")

    def test_a_restricted_agent_entry_fails(self):
        """TSK-2700 criterion 3, REQ-3270: Agent with a restriction still dispatches, so Agent(worker) fails."""
        self.refuses(SHIPPED_AGENT, agent(tools='[Read, "Agent(worker)"]'), "tools")

    def test_agent_in_a_comma_separated_list_fails(self):
        """TSK-2700 criterion 3, REQ-3270: tools is read as a comma-separated string as well as a list."""
        self.refuses(SHIPPED_AGENT, agent(tools="Read, Agent, Grep"), "tools")

    def test_front_matter_that_does_not_parse_fails_alone(self):
        """TSK-2700 criterion 4, REQ-2974, REQ-3270: front matter that doesn't parse fails with that reason, and no field rule runs."""
        done = self.refuses(SHIPPED_AGENT, agent(tools="[Read, Grep"), "front matter")
        failures = [line for line in done.stdout.splitlines() if line.startswith(SHIPPED_AGENT)]
        self.assertEqual(len(failures), 1, done.stdout)
        for field in AGENT_FIELDS:
            self.assertNotIn(field, failures[0], done.stdout)

    def test_an_agent_declaring_all_six_passes(self):
        """TSK-2700 criterion 5, REQ-2974, REQ-2982, REQ-2984, REQ-2988, REQ-3270: all six with skills [] pass."""
        self.refuses(SHIPPED_AGENT, agent(omitClaudeMd=None), "omitClaudeMd")
        self.passes(SHIPPED_AGENT, agent(skills="[]"))

    def test_a_shipped_agent_with_no_tools_passes(self):
        """TSK-2700 criterion 5, REQ-3270: tools [] grants no tool, so it passes."""
        self.refuses(SHIPPED_AGENT, agent(tools="[]", effort=None), "effort")
        self.passes(SHIPPED_AGENT, agent(tools="[]"))

    def test_a_full_model_identifier_passes(self):
        """TSK-2700 criterion 5, REQ-2988: a value containing claude- is a full identifier, so it passes."""
        self.refuses(SHIPPED_AGENT, agent(model="claude-opus-5-5", maxTurns=None), "maxTurns")
        self.passes(SHIPPED_AGENT, agent(model="claude-opus-5-5"))

    def test_a_repositorys_own_agent_may_list_agent(self):
        """TSK-2700 criterion 5, REQ-3270: the tools rule binds a unit's agents, not a repository's own."""
        self.refuses(OWN_AGENT, agent(tools="[Read, Agent]", skills=None), "skills", ".claude")
        self.passes(OWN_AGENT, agent(tools="[Read, Agent]"), ".claude")

    def test_a_repositorys_own_agent_may_list_every_tool(self):
        """TSK-2700 criterion 5, REQ-3270: a repository's own agent may write tools "*"."""
        self.refuses(OWN_AGENT, agent(tools='"*"', model=None), "model", ".claude")
        self.passes(OWN_AGENT, agent(tools='"*"'), ".claude")


class AgentOutcomes(unittest.TestCase):
    """TSK-2702, REQ-0816, SPC-1030 "The check": an agent in a unit's `agents/` directory names the four outcomes
    in its body, and a failure names the file and each missing word."""

    def check(self, path, text, *paths):
        repository = Repository({path: text})
        self.addCleanup(repository.tmp.cleanup)
        return repository.check(*paths)

    def missing(self, done, path):
        """The outcome words the check's failure lines for `path` name, read from the lines naming no field."""
        lines = [line for line in done.stdout.splitlines() if line.startswith(path)]
        words = set()
        for line in lines:
            words.update(w for w in OUTCOMES if re.search(rf"(?<![A-Z_]){w}(?![A-Z_])", line))
        return words

    def test_a_unit_agent_naming_no_outcome_fails_naming_each_word(self):
        """TSK-2702 criterion 1, REQ-0816: a unit's agent naming none of the four fails, naming the file and all
        four words."""
        done = self.check(SHIPPED_AGENT, agent(role="You review the demo."))
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.missing(done, SHIPPED_AGENT), set(OUTCOMES), done.stdout)

    def test_a_unit_agent_missing_only_blocked_fails_naming_blocked(self):
        """TSK-2702 criterion 1, REQ-0816: a unit's agent naming all but BLOCKED fails, naming the file and
        BLOCKED alone."""
        role = "You review the demo and end with outcome: DONE, DONE_WITH_CONCERNS or NEEDS_CONTEXT."
        done = self.check(SHIPPED_AGENT, agent(role=role))
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.missing(done, SHIPPED_AGENT), {"BLOCKED"}, done.stdout)

    def test_a_unit_agent_missing_only_done_fails_naming_done(self):
        """TSK-2702 criterion 1, REQ-0816: DONE_WITH_CONCERNS doesn't count as naming DONE, so an agent naming
        the other three fails, naming DONE."""
        role = "You review the demo and end with outcome: DONE_WITH_CONCERNS, NEEDS_CONTEXT or BLOCKED."
        done = self.check(SHIPPED_AGENT, agent(role=role))
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(self.missing(done, SHIPPED_AGENT), {"DONE"}, done.stdout)

    def test_a_unit_agent_naming_all_four_passes(self):
        """TSK-2702 criterion 1, REQ-0816: a unit's agent naming all four passes."""
        done = self.check(SHIPPED_AGENT, agent())
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 authoring failures", done.stdout)

    def test_a_repositorys_own_agent_naming_none_passes(self):
        """TSK-2702 criterion 1, REQ-0816: a repository's own agent under `.claude/agents/` isn't read for the
        outcome rule. The same text in a unit fails, so this passing isn't a check that reads nothing."""
        self.assertEqual(self.check(SHIPPED_AGENT, agent(role="You review the demo.")).returncode, 1)
        done = self.check(OWN_AGENT, agent(role="You review the demo."), ".claude")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 authoring failures", done.stdout)


class Cost(unittest.TestCase):
    """ADR-1460: meow-author cost reports each unit's cost against its budget."""

    def repo(self, budget="permanent_characters = 200\n", description="The demo skill. It MUST be loaded before a demo is run.", when=""):
        skill = GOOD.replace("description: The demo skill. It MUST be loaded before a demo is run.", f"description: {description}" + (f"\nwhen_to_use: {when}" if when else ""))
        files = unit(skill, {"plugins/meow-demo/.claude-plugin/plugin.json": '{"name": "meow-demo"}\n'})
        if budget is not None:
            files["plugins/meow-demo/budget.toml"] = budget
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository.run_cost()

    def test_a_unit_within_its_budget_passes_and_names_skill_doctor(self):
        """REQ-1072: the report gives each unit's cost, and names where its use is reported."""
        done = self.repo()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meow-demo: 55 of 200 characters on every turn", done.stdout)
        self.assertIn("/skill-doctor", done.stdout)

    def test_a_unit_over_its_budget_fails(self):
        """REQ-1072, REQ-1074: the cost report fails the gate on an overrun."""
        done = self.repo(budget="permanent_characters = 10\n")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("meow-demo: loads 55 characters on every turn, 45 over its budget of 10", done.stdout)

    def test_a_unit_with_no_budget_fails(self):
        """REQ-1074: every unit states the budget it is held to."""
        done = self.repo(budget=None)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("meow-demo: states no budget in budget.toml", done.stdout)

    def test_a_description_and_when_to_use_over_the_cap_fail(self):
        """REQ-1072: the platform caps a description and its when_to_use together."""
        done = self.repo(budget="permanent_characters = 5000\n", description="x" * 1000, when="y" * 600)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("description is 1601 characters, over the cap of 1536", done.stdout)


class Launcher(unittest.TestCase):
    """SPC-1080, BUG-1240: a launcher with no binary beside it reports each subcommand unchecked, never passed."""

    def test_a_missing_binary_is_unchecked_and_names_the_machine_and_the_reinstall(self):
        machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
        for subcommand in ["check", "cost"]:
            with self.subTest(subcommand=subcommand), tempfile.TemporaryDirectory() as tmp:
                launcher = Path(tmp) / "bin" / "meow-author"
                launcher.parent.mkdir()
                launcher.write_text(BIN.read_text(encoding="utf-8"), encoding="utf-8")
                launcher.chmod(0o755)
                done = subprocess.run(["sh", str(launcher), subcommand], cwd=tmp, capture_output=True, text=True, input="")
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertIn(f"meow-author {subcommand}: unchecked: ", done.stdout)
                self.assertIn(machine, done.stdout)
                self.assertIn("reinstall the unit", done.stdout)


def rules(text):
    """Each numbered rule under a `<rules>` tag, as (identifier, text), the text lower case with backticks
    kept and every run of white space one space, so a wrapped rule reads as one line."""
    found = []
    for block in re.findall(r"<rules\b[^>]*>(.*?)</rules>", text, re.DOTALL):
        for ident, body in re.findall(r"^- ([A-Z]+\d+)\.\s(.*?)(?=^- [A-Z]+\d+\.\s|\Z)", block, re.MULTILINE | re.DOTALL):
            found.append((ident, re.sub(r"\s+", " ", body).strip().lower()))
    return found


class WriteSkill(unittest.TestCase):
    """ADR-1700, SPC-1030: the write skill carries the delegation rules no program can check, each a numbered
    rule under a `<rules>` tag that states its reason."""

    # REQ-2972: knowledge ships as a skill, and never as an agent.
    KNOWLEDGE = (r"\bknowledge\b", r"\bas a skill\b[^.;]*\bnever as an agent\b")
    # REQ-2976: a delegated agent is no boundary that contains what it does.
    BOUNDARY = (r"\bagent\b", r"\b(never|not|no)\b[^.;,]*\bboundary\b", r"\bsandbox\b")

    @staticmethod
    def matches(body, patterns):
        return "because" in body and all(re.search(p, body) for p in patterns)

    def rule(self, *patterns):
        """The rules matching every pattern and stating a reason, or a failure naming what was looked for."""
        text = (UNIT / "skills" / "write" / "SKILL.md").read_text(encoding="utf-8")
        matching = [ident for ident, body in rules(text) if self.matches(body, patterns)]
        self.assertTrue(matching, f"no rule under <rules> in the write skill matches {patterns} and states a reason")
        return matching

    def test_knowledge_ships_as_a_skill_and_never_as_an_agent(self):
        """TSK-2701 criterion 1, REQ-2972: knowledge ships as a skill loaded into the working context, never as
        an agent."""
        self.rule(*self.KNOWLEDGE)

    def test_an_agent_a_unit_ships_carries_the_denial_rule(self):
        """TSK-2703 criterion 1, REQ-2978: the rule beside D9 has an agent a unit ships name the four outcomes and
        carry the denial rule, and states its reason."""
        found = self.rule(r"\bdone_with_concerns\b", r"\bneeds_context\b", r"\bblocked\b", r"\bdenial rule\b")
        text = (UNIT / "skills" / "write" / "SKILL.md").read_text(encoding="utf-8")
        idents = [ident for ident, _ in rules(text)]
        self.assertIn("D9", idents)
        self.assertIn(idents[idents.index("D9") + 1], found)

    def test_the_knowledge_rule_refuses_its_inversion(self):
        """REQ-2972: the words alone don't pass, so a rule saying the opposite fails the fixture above."""
        for inverted in (
            "knowledge is not a skill; ship it as an agent, because an agent keeps it out of the context.",
            "ship knowledge as an agent and never as a skill, because an agent keeps it out of the context.",
        ):
            with self.subTest(rule=inverted):
                self.assertFalse(self.matches(inverted, self.KNOWLEDGE))

    def test_a_delegated_agent_is_no_isolation_boundary(self):
        """TSK-2701 criterion 1, REQ-2976: no text treats a delegated agent as an isolation boundary, because it
        runs under the parent's sandbox configuration."""
        self.rule(*self.BOUNDARY)

    def test_the_boundary_rule_refuses_its_inversion(self):
        """REQ-2976: the words alone don't pass, so a rule saying the opposite fails the fixture above."""
        for inverted in (
            "treat a delegated agent as an isolation boundary, because it has its own sandbox.",
            "describe a delegated agent as a boundary, because it doesn't share the parent's sandbox.",
        ):
            with self.subTest(rule=inverted):
                self.assertFalse(self.matches(inverted, self.BOUNDARY))

    def test_each_of_the_six_fields_has_its_rule(self):
        """TSK-2701 criterion 1: one rule for each of the six fields SPC-1030 states under "What an agent
        declares", with the reason ADR-1700 gives: maxTurns REQ-2974, tools REQ-3270, model and effort REQ-2988,
        omitClaudeMd REQ-2982, skills REQ-2984."""
        fields = {
            "maxTurns": r"\bceiling\b",
            "tools": r"`agent`",
            "model": r"`inherit`",
            "effort": r"`xhigh`",
            "omitClaudeMd": r"\binstructions\b",
            "skills": r"\bpreload",
        }
        for field, reason in fields.items():
            with self.subTest(field=field):
                self.rule(re.escape(f"`{field.lower()}`"), reason)

    def test_a_partial_output_is_unfinished(self):
        """TSK-2701 criterion 1, REQ-2974: a dispatcher reads an output marked partial as unfinished work."""
        self.rule(r"\bdispatch", r"\bpartial\b", r"\bunfinished\b")


if __name__ == "__main__":
    unittest.main()
