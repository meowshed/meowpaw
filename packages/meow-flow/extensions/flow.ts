// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-flow extension for Pi.
 *
 * Reports what waits at a gate when a session starts, offers the router as
 * a tool, and registers a command for each method step and driver. The
 * guards live in the units that own them (ADR-2820): meow-git's in
 * meow-git, the governance guard in meow-github, the loop guard in
 * meow-loop.
 */

import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "typebox";

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
  ctx: Pick<ExtensionContext, "modelRegistry">,
  systemPrompt: string,
  userPrompt: string,
): Promise<string> {
  const models = await ctx.modelRegistry.getAvailableOfType("chat");
  const model =
    models.find((m) => m.provider === "anthropic" && /sonnet/i.test(m.id)) ??
    models[0];
  if (!model) throw new Error("no available chat model");
  const message = await ctx.modelRegistry.completeSimple(model, {
    systemPrompt,
    messages: [{ role: "user", content: userPrompt }],
  });
  return message.content
    .filter((b): b is { type: "text"; text: string } => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
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

      return { content: route, details: undefined };
    },
  });

  // One command per step and driver, each loading its skill.
  const commands: ReadonlyArray<readonly [string, string]> = [
    ["meow-flow:research", "Run the research step"],
    ["meow-flow:requirements", "Run the requirements step"],
    ["meow-flow:design", "Run the design step"],
    ["meow-flow:spec", "Run the spec step"],
    ["meow-flow:epic", "Run the epic step"],
    ["meow-flow:implement", "Run the implement step"],
    ["meow-flow:review", "Run the review step"],
    ["meow-flow:run", "Drive the method to the next approval gate"],
    ["meow-flow:init", "Initialise a repository with a profile and constitution"],
    ["meow-flow:onboard", "Bring a repository's existing documents into the record"],
  ];

  for (const [name, description] of commands) {
    pi.registerCommand(name, {
      description,
      handler: async (_args, ctx) => {
        ctx.ui.notify(`Load the skill /${name} and follow its instructions`, "info");
      },
    });
  }
}