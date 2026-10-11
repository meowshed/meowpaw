// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-flow extension for Pi.
 *
 * Reports what waits at a gate when a session starts, registers a command
 * for each method step and driver, each sending its skill into the session,
 * and registers the researcher, whose nested call drafts the research
 * record's body from the material the step gathers (REQ-3526). The route
 * needs no dispatch: the session classifies under the route skill (ADR-2930).
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "typebox";
import { answerWith, pickModels, responseText } from "../lib/models.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");
const binDir = join(packageRoot, "bin");
const promptsDir = join(packageRoot, "prompts");

function runBinary(
  binary: string,
  args: string[],
  timeout: number,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    execFile(binary, args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
  });
}

async function readBundled(relative: string): Promise<string> {
  try {
    return await readFile(join(packageRoot, relative), "utf-8");
  } catch {
    return "";
  }
}

/** Run one nested model call on the cheap tier, or name the model that failed. */
async function nestedCall(
  ctx: Pick<ExtensionContext, "modelRegistry" | "model">,
  systemPrompt: string,
  userPrompt: string,
): Promise<{ ok: true; text: string } | { ok: false; reason: string }> {
  const models = await ctx.modelRegistry.getAvailableOfType("chat");
  return answerWith(
    pickModels(models, ctx.model, process.env.MEOW_NESTED_MODEL ?? "glm-5.3-flash"),
    async (model) => {
      const message = await ctx.modelRegistry.completeSimple(model, {
        systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      });
      const text = responseText(message);
      if (!text.ok) throw new Error(text.reason);
      return text.text;
    },
  );
}

export default async function (pi: ExtensionAPI) {
  // The skills call the bundled wrapper by name.
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

  // The reply shape here feeds only the researcher's nested model call,
  // because a nested call runs its own prompt and never sees the kernel's
  // injection (REQ-4134).
  const replyShape = await readBundled("prompts/reply-shape.md");
  const researchTemplate = await readBundled("templates/research.md");

  // Report what waits at a gate when a session starts. Best-effort: a
  // session starts regardless.
  pi.on("session_start", async (_event, ctx) => {
    const { stdout } = await runBinary(join(binDir, "paw"), ["status", "--waiting"], 30_000);
    if (stdout.trim() && ctx.hasUI) {
      ctx.ui.notify(stdout.trim(), "info");
    }
  });

  // The researcher: the research step gathers the material, this call drafts
  // the record's body from it, and the session writes the artifact and runs
  // the checks (REQ-3526). A nested call reads nothing, so the material
  // carries everything the draft rests on.
  pi.registerTool({
    name: "meow-research",
    label: "Researcher",
    description:
      "Drafts a research record's body from the question and material the research step passes, reading nothing; the session writes the artifact, runs the checks and stops at the gate.",
    parameters: Type.Object({
      question: Type.String({ description: "The research question" }),
      material: Type.String({
        description:
          "The material gathered: the record template, the searches with their results, and the text of every source the draft may cite",
      }),
    }),
    execute: async (args, ctx) => {
      if (!replyShape || !researchTemplate || !ctx.modelRegistry) {
        return {
          content:
            "Researcher unavailable: the reply shape, the template or the model registry is not loaded",
          details: undefined,
        };
      }
      const draft = await nestedCall(
        ctx,
        replyShape,
        [
          "You are a researcher drafting one record of a method's record.",
          "Write the record's body from the material alone: one finding per",
          "claim, each with its source and the date you read it; a method",
          "section recording what was read, run and searched; at least three",
          "options compared where the question admits them, with the case",
          "against the one you lead with; and numbered conclusions, each an",
          "obligation that follows from a finding. Drop any claim the material",
          "doesn't carry, and cite no requirement.",
          "",
          "The record template:",
          "",
          researchTemplate,
          "",
          `The question: ${args.question}`,
          "",
          "The material:",
          "",
          args.material,
        ].join("\n"),
      );
      return { content: draft.ok ? draft.text : draft.reason, details: undefined };
    },
  });

  // One command per step and driver, each sending its skill into the
  // session, because a notification reaches only the person (REQ-4122).
  const commands: ReadonlyArray<readonly [string, string, string]> = [
    ["meow-flow:research", "Run the research step", "method"],
    ["meow-flow:requirements", "Run the requirements step", "method"],
    ["meow-flow:design", "Run the design step", "method"],
    ["meow-flow:spec", "Run the spec step", "method"],
    ["meow-flow:epic", "Run the epic step", "method"],
    ["meow-flow:implement", "Run the implement step", "method"],
    ["meow-flow:review", "Run the review step", "method"],
    ["meow-flow:run", "Drive the method to the next approval gate", "run"],
    ["meow-flow:init", "Initialise a repository with a profile and constitution", "init"],
    ["meow-flow:onboard", "Bring a repository's existing documents into the record", "onboard"],
  ];

  for (const [name, description, skill] of commands) {
    pi.registerCommand(name, {
      description,
      handler: async (args, ctx) => {
        const file = join(packageRoot, "skills", skill, "SKILL.md");
        let body: string;
        try {
          body = await readFile(file, "utf-8");
        } catch {
          if (ctx.hasUI) {
            ctx.ui.notify(`meow-flow: ${file} is missing, so /${name} loads nothing`, "warning");
          }
          return;
        }
        pi.sendUserMessage(
          `${body}\n\nYou are running this skill from the /${name} command. Its arguments, as the person typed them: ${args || "(none)"}. Carry out the skill's instructions now.`,
        );
      },
    });
  }
}