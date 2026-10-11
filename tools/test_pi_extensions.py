# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The Pi extensions load a command's skill, start a loop run from the session, and answer or name the router's failure (BUG-1600, BUG-1610, BUG-1620)."""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOW = ROOT / "packages" / "meow-flow"
LOOP = ROOT / "packages" / "meow-loop"

FLOW_COMMANDS = [
    ("meow-flow:research", "method"),
    ("meow-flow:requirements", "method"),
    ("meow-flow:design", "method"),
    ("meow-flow:spec", "method"),
    ("meow-flow:epic", "method"),
    ("meow-flow:implement", "method"),
    ("meow-flow:review", "method"),
    ("meow-flow:run", "run"),
    ("meow-flow:init", "init"),
    ("meow-flow:onboard", "onboard"),
]

NODE_CHECK = """
import { pickModels, responseText, answerWith } from "<file>";

const assert = (ok, why) => {
  if (!ok) {
    console.error("FAIL: " + why);
    process.exit(1);
  }
};

const openrouterClaude = { provider: "openrouter", id: "anthropic/claude-sonnet-5.5" };
const xiaomi = { provider: "xiaomi-token-plan-ams", id: "mimo-v2.5-pro" };

const picked = pickModels([xiaomi, openrouterClaude], xiaomi);
assert(picked[0] === openrouterClaude, "a Claude model under another provider is not picked first: " + JSON.stringify(picked));

const glm = { provider: "openrouter", id: "z-ai/glm-5.3-flash" };
const preferred = pickModels([xiaomi, openrouterClaude, glm], xiaomi, "glm-5.3-flash");
assert(preferred[0] === glm, "the model MEOW_ROUTER_MODEL names is not picked first: " + JSON.stringify(preferred));
assert(preferred[1] === openrouterClaude, "the Claude model is not second after the preference: " + JSON.stringify(preferred));

assert(responseText({ content: " route " }).ok && responseText({ content: " route " }).text === "route", "a string content yields its text");
assert(responseText({ content: [{ type: "text", text: "route" }] }).text === "route", "a block list yields its text");
assert(!responseText({ stopReason: "error", errorMessage: "boom" }).ok, "an error message fails the model");
assert(!responseText(undefined).ok, "a missing message fails");

const calls = [];
const result = await answerWith([xiaomi, openrouterClaude], async (m) => {
  calls.push(m.id);
  if (m === xiaomi) throw new Error("content.some is not a function");
  return "route: reduced";
});
assert(result.ok && result.text === "route: reduced", "a failing model is skipped and the next answers");
assert(calls.join() === "mimo-v2.5-pro,anthropic/claude-sonnet-5.5", "the candidates run in the picked order: " + calls.join());

const none = await answerWith([xiaomi], async () => {
  throw new Error("content.some is not a function");
});
assert(!none.ok, "a catalogue where every model throws answers not ok");
assert(none.reason.includes("xiaomi-token-plan-ams/mimo-v2.5-pro"), "the failure names its provider and model: " + none.reason);
assert(none.reason.includes("content.some is not a function"), "the failure names the reason: " + none.reason);

console.log("NODE OK");
"""


class FlowCommands(unittest.TestCase):
    def setUp(self):
        self.text = (FLOW / "extensions" / "flow.ts").read_text(encoding="utf-8")

    def test_each_command_maps_to_a_skill_that_exists(self):
        """TSK-5440 criterion 2: the skill file each command names exists."""
        for name, skill in FLOW_COMMANDS:
            with self.subTest(command=name):
                self.assertIn(
                    f'"{name}"', self.text,
                    f"/{name} is not registered",
                )
                self.assertTrue(
                    (FLOW / "skills" / skill / "SKILL.md").is_file(),
                    f"/{name} maps to skills/{skill}/SKILL.md, which is missing",
                )

    def test_each_command_sends_its_skill_into_the_session(self):
        """TSK-5440 criterion 1, REQ-4122: no handler ends at a notification."""
        handler = re.search(
            r"handler: async \(args, ctx\) => \{(.*?)\n      \},",
            self.text,
            re.S,
        )
        self.assertIsNotNone(handler, "the commands share no handler")
        body = handler.group(1)
        self.assertIn("pi.sendUserMessage(", body, "the handler sends nothing into the session")
        self.assertIn("SKILL.md", body, "the handler names no skill file")
        self.assertNotIn("Load the skill /", body, "the handler still tells the person to load a skill")
        self.assertNotIn("ctx.ui.notify(`Load", body, "the handler still notifies alone")

    def test_the_router_uses_the_shared_answer_loop(self):
        """TSK-5460: the tool answers through the module the test drives."""
        self.assertIn("from \"../lib/router.mjs\"", self.text, "flow.ts imports no router module")
        self.assertIn("answerWith(pickModels(models, ctx.model, process.env.MEOW_ROUTER_MODEL)", self.text, "the nested call runs no candidate loop")
        self.assertIn("route.ok ? route.text : route.reason", self.text, "the tool surfaces neither the text nor the reason")


class LoopRun(unittest.TestCase):
    def setUp(self):
        self.text = (LOOP / "extensions" / "loop.ts").read_text(encoding="utf-8")

    def test_the_start_command_is_registered_and_reaches_the_runner(self):
        """TSK-5450 criterion 1: /meow-loop:run starts a run through `prompt`."""
        self.assertIn('pi.registerCommand("meow-loop:run"', self.text, "no run command is registered")
        block = self.text[self.text.index('pi.registerCommand("meow-loop:run"'):]
        self.assertIn('["prompt"]', block, "the command runs no prompt subcommand")
        self.assertIn('"UserPromptSubmit"', block, "the command names no hook event")
        self.assertIn("session_id: sessionId(ctx)", block, "the command names no session id")
        self.assertIn("cwd: ctx.cwd", block, "the command names no working directory")
        self.assertIn("pi.sendUserMessage(answer.additionalContext)", block, "the start context reaches no session")

    def test_other_input_reaches_the_runner(self):
        """TSK-5450 criterion 2: the person's next prompt ends a run `cancelled`."""
        block = self.text[self.text.index('pi.on("input"'):]
        self.assertIn('["prompt"]', block, "other input reaches no subcommand")
        self.assertIn('event.source === "extension"', block, "the extension's own messages are not excluded")
        self.assertIn('{ action: "continue" }', block, "the input is not let through")

    def test_the_settle_boundary_carries_the_frozen_prompt(self):
        """TSK-5450 criterion 3: `stop` decides, and a block continues once."""
        block = self.text[self.text.index('pi.on("agent_before_settle"'):]
        self.assertIn('["stop"]', block, "the boundary runs no stop subcommand")
        self.assertIn('event.outcome === "aborted"', block, "an escaped turn is not left alone")
        self.assertIn('answer.decision === "block"', block, "the boundary reads no block decision")
        self.assertIn('"custom_message"', block, "the frozen prompt enters as no message")
        self.assertIn("continue: true", block, "the boundary continues nothing")


class RouterModule(unittest.TestCase):
    def test_the_module_answers_across_providers_and_names_its_failure(self):
        """TSK-5460 criteria 1 to 3: the module's behaviour, driven by node."""
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as handle:
            handle.write(NODE_CHECK.replace("<file>", (FLOW / "lib" / "router.mjs").as_uri()))
            script = Path(handle.name)
        try:
            run = subprocess.run(
                ["node", "--input-type=module", "-e", f'await import({str(script.as_uri())!r})'],
                capture_output=True,
                text=True,
                timeout=60,
            )
        finally:
            script.unlink(missing_ok=True)
        self.assertEqual(run.returncode, 0, f"node reported: {run.stderr.strip() or run.stdout.strip()}")
        self.assertIn("NODE OK", run.stdout)


if __name__ == "__main__":
    unittest.main()