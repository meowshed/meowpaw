# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The reviewer's labelled set holds a case for every rule of the writing standard that a text can show
(REQ-4800), a test fails and names a rule with none (REQ-4802), and the rules no text can show are listed with
their reason (REQ-4804)."""

import re
import tomllib
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
RULE_FILES = (
    UNIT / "skills" / "writing" / "SKILL.md",
    UNIT / "skills" / "writing" / "documents.md",
)
EVALS = UNIT / "evals"
EXEMPT = EVALS / "rule-cases.toml"
RULE = re.compile(r"^- ([A-Z][0-9]+)\.", re.MULTILINE)
TAG = re.compile(r"^tags:\s*\[(.*)\]\s*$", re.MULTILINE)


def rules():
    """The identifiers of the rules the standard states, from both files that keep them."""
    found = set()
    for path in RULE_FILES:
        found.update(RULE.findall(path.read_text(encoding="utf-8")))
    return found


def tagged(evals=EVALS):
    """The rules each reviewer case tests, by the `rule-<ID>` tags in its prompt."""
    cases = {}
    for prompt in sorted(evals.glob("*/prompt.md")):
        match = TAG.search(prompt.read_text(encoding="utf-8"))
        if not match:
            continue
        for tag in (t.strip() for t in match.group(1).split(",")):
            if tag.startswith("rule-"):
                cases.setdefault(tag[len("rule-"):], []).append(prompt.parent.name)
    return cases


def exempt(path=EXEMPT):
    with path.open("rb") as handle:
        return tomllib.load(handle).get("exempt", {})


def uncovered(stated, cases, listed):
    """The rules with neither a case nor an entry in the list."""
    return sorted(r for r in stated if r not in cases and r not in listed)


class RuleCases(unittest.TestCase):
    """TSK-5330, REQ-4800, REQ-4802, REQ-4804."""

    def test_every_rule_has_a_case_or_an_entry(self):
        """TSK-5330 criterion 1, REQ-4800: no rule of the standard is without a case or an entry."""
        missing = uncovered(rules(), tagged(), exempt())
        self.assertEqual(missing, [], f"rules with no case and no entry in rule-cases.toml: {missing}")

    def test_a_rule_with_no_case_is_named(self):
        """TSK-5330 criterion 2, REQ-4802: a rule added with no case is the one the check names."""
        stated = rules() | {"Z99"}
        self.assertEqual(uncovered(stated, tagged(), exempt()), ["Z99"])

    def test_an_entry_names_a_rule_with_no_case(self):
        """TSK-5330 criterion 3, REQ-4804: an entry for a rule that has a case, or that the standard no longer
        states, hides a gap and fails."""
        cases, stated = tagged(), rules()
        stale = sorted(r for r in exempt() if r in cases or r not in stated)
        self.assertEqual(stale, [], f"entries that name a rule with a case or no rule: {stale}")

    def test_a_case_names_a_rule_the_standard_states(self):
        """TSK-5330 criterion 1, REQ-4800: a tag for a rule that doesn't exist tests nothing."""
        unknown = sorted(r for r in tagged() if r not in rules())
        self.assertEqual(unknown, [], f"cases tagged with a rule the standard doesn't state: {unknown}")

    def test_a_rule_case_is_shaped_like_the_others(self):
        """TSK-5330 criterion 4: a rule case asks for the review and its grader names the rule."""
        for rule, names in tagged().items():
            for name in names:
                case = EVALS / name
                prompt = (case / "prompt.md").read_text(encoding="utf-8")
                self.assertIn("meow-prose:prose", prompt, name)
                self.assertIn("<text>", prompt, name)
                graders = sorted((case / "graders").glob("*.md"))
                self.assertTrue(graders, f"{name} has no grader")
                text = "\n".join(g.read_text(encoding="utf-8") for g in graders)
                self.assertIn(f"({rule})", text, f"{name}: its grader doesn't name {rule}")


if __name__ == "__main__":
    unittest.main()
