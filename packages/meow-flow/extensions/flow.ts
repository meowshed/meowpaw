// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-flow extension for Pi.
 *
 * Reports what waits at a gate when a session starts, offers the router as
 * a tool, and registers a command for each method step and driver, each
 * sending its skill into the session. The guards live in the units that own
 * them (ADR-2820): meow-git's in meow-git, the governance guard in
 * meow-github, the loop guard in meow-loop.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "typebox";
import { answerWith, pickModels, responseText } from "../lib/router.mjs";

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

async function readPrompt(name: string): Promise<string> {
  try {
    return await readFile(join(promptsDir, name), "utf-8");
  } catch {
    return "";
  }
}

/** Run one nested model call with the reply shape as its system prompt. */
async function nestedCall(
  ctx: Pick<ExtensionContext, "modelRegistry" | "model">,
  systemPrompt: string,
  userPrompt: string,
): Promise<{ ok: true; text: string } | { ok: false; reason: string }> {
  const models = await ctx.modelRegistry.getAvailableOfType("chat");
  return answerWith(pickModels(models, ctx.model, process.env.MEOW_ROUTER_MODEL), async (model) => {
    const message = await ctx.modelRegistry.completeSimple(model, {
      systemPrompt,
      messages: [{ role: "user", content: userPrompt }],
    });
    const text = responseText(message);
    if (!text.ok) throw new Error(text.reason);
    return text.text;
  });
}

export default async function (pi: ExtensionAPI) {
  // The skills call the bundled wrapper by name.
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

  // The reply shape here feeds only the router's nested model call, because
  // a nested call runs its own prompt and never sees the kernel's injection.
  const replyShape = await readPrompt("reply-shape.md");
  const routerPrompt = await readPrompt("router.md");

  // Report what waits at a gate when a session starts. Best-effort: a
  // session starts regardless.
  pi.on("session_start", async (_event, ctx) => {
    const { stdout } = await runBinary(join(binDir, "paw"), ["status", "--waiting"], 30_000);
    if (stdout.trim() && ctx.hasUI) {
      ctx.ui.notify(stdout.trim(), "info");
    }
  });

  // The router: one nested, read-only model call that reports the route.
  pi.registerTool({
    name: "meow-router",
    label: "Router",
    description:
      "Route a request to change the repository before work starts, and report the route and its reason before any edit.",
    parameters: Type.Object({
      request: Type.String({ description: "The request to route" }),
    }),
    execute: async (args, ctx) => {
      if (!routerPrompt || !ctx.modelRegistry) {
        return {
          content: "Router unavailable: agent prompt or model registry not loaded",
          details: undefined,
        };
      }

      const route = await nestedCall(
        ctx,
        replyShape,
        `${routerPrompt}\n\nRequest: ${args.request}`,
      );

      return { content: route.ok ? route.text : route.reason, details: undefined };
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