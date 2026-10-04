// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw method extension for Pi.
 *
 * Puts the package's bin wrappers on PATH, reports what waits at a gate
 * when a session starts, holds the git, governance and loop guards over
 * every command and write the model runs, offers the router as a tool, and
 * registers a command for each method step and driver. Every guard reads
 * the hook JSON on standard input: exit 0 allows, exit 2 blocks, and the
 * governance guard answers with a permission decision on standard output
 * (SPC-1300, ADR-2790).
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

/**
 * Run a guard binary with the hook JSON on standard input, the one contract
 * every meow guard reads.
 */
function runGuard(
  binary: string,
  args: string[],
  hookEvent: object,
  timeout: number,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = execFile(binary, args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
    child.stdin?.end(JSON.stringify(hookEvent));
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

/** The permission decision a guard printed, or undefined where it stayed silent. */
function decision(stdout: string): { decision: string; reason: string } | undefined {
  const match = stdout.match(/"permissionDecision":\s*"(ask|deny)"/);
  if (!match) return undefined;
  const reason = stdout.match(/"permissionDecisionReason":\s*"((?:[^"\\]|\\.)*)"/);
  return { decision: match[1], reason: reason?.[1]?.replace(/\\n/g, "\n") ?? "" };
}

const GIT_COMMIT_PATTERN = /\bgit\s+commit\b/;
const GIT_PUSH_PATTERN = /\bgit\s+push\b/;

export default async function (pi: ExtensionAPI) {
  // The skills call the bundled wrappers by name, so put them on PATH for
  // the Bash tool the way Claude Code does natively for a plugin's bin/.
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

  // The reply shape here feeds only the router's nested model call, because
  // a nested call runs its own prompt and never sees the kernel's injection.
  const replyShape = await readPrompt("reply-shape.md");
  const routerPrompt = await readPrompt("router.md");

  // Report what waits at a gate when a session starts, as meow-flow's
  // SessionStart hook does. Best-effort: a session starts regardless.
  pi.on("session_start", async (_event, ctx) => {
    const { stdout } = await runGuard(
      join(binDir, "paw"), ["status", "--waiting"],
      {}, 30_000,
    );
    if (stdout.trim() && ctx.hasUI) {
      ctx.ui.notify(stdout.trim(), "info");
    }
  });

  /** One guard's verdict for a Bash command: block with a reason, or pass. */
  async function bashGuards(command: string, ctx: { hasUI: boolean; ui: { confirm(q: string): Promise<boolean> } }): Promise<string | undefined> {
    if (GIT_COMMIT_PATTERN.test(command)) {
      const { exitCode, stderr, stdout } = await runGuard(
        join(binDir, "meow-git"), ["commit-guard"],
        { tool_name: "Bash", tool_input: { command } }, 30_000,
      );
      if (exitCode !== 0) {
        return stderr.trim() || stdout.trim() || "Commit blocked by meow-git";
      }
    }

    if (GIT_PUSH_PATTERN.test(command)) {
      const { exitCode, stderr, stdout } = await runGuard(
        join(binDir, "meow-git"), ["push-guard"],
        { tool_name: "Bash", tool_input: { command } }, 120_000,
      );
      if (exitCode !== 0) {
        return stderr.trim() || stdout.trim() || "Push blocked by meow-git";
      }
    }

    // The governance guard asks a person before a gh command changes how
    // the repository is governed; where there is no one to ask, it denies.
    if (/\bgh\s/.test(command) && !/\bgh\s+(?:api|auth|help|version)\b/.test(command)) {
      const { stdout } = await runGuard(
        join(binDir, "meow-github"), ["governance-guard"],
        { tool_name: "Bash", tool_input: { command } }, 10_000,
      );
      const asked = decision(stdout);
      if (asked?.decision === "ask") {
        const allow = ctx.hasUI ? await ctx.ui.confirm(`${asked.reason}\n\nAllow?`) : false;
        if (!allow) return asked.reason;
      }
    }

    // The loop guard keeps a run inside its own step and its own state.
    const { stdout } = await runGuard(
      join(binDir, "meow-loop"), ["guard"],
      { tool_name: "Bash", tool_input: { command } }, 10_000,
    );
    const denied = decision(stdout);
    if (denied?.decision === "deny") return denied.reason;

    return undefined;
  }

  /** The loop guard's verdict for a file write: block with a reason, or pass. */
  async function writeGuard(toolName: string, filePath: string): Promise<string | undefined> {
    const { stdout } = await runGuard(
      join(binDir, "meow-loop"), ["guard"],
      { tool_name: toolName, tool_input: { file_path: filePath } }, 10_000,
    );
    const denied = decision(stdout);
    if (denied?.decision === "deny") return denied.reason;
    return undefined;
  }

  // The model's Bash commands.
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName === "bash") {
      const command = commandOf(event);
      const reason = await bashGuards(command, ctx);
      if (reason !== undefined) return { block: true, reason };
      return undefined;
    }

    if (event.toolName === "edit" || event.toolName === "write") {
      const filePath = filePathOf(event);
      if (typeof filePath !== "string") return undefined;
      const reason = await writeGuard(event.toolName, filePath);
      if (reason !== undefined) return { block: true, reason };
      return undefined;
    }

    return undefined;
  });

  // A command the person types with ! in front of it.
  pi.on("user_bash", async (event, ctx) => {
    const reason = await bashGuards(event.command, ctx);
    if (reason === undefined) return undefined;

    return {
      result: { output: reason, exitCode: 126, cancelled: false, truncated: false },
    };
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

function commandOf(event: { input?: { command?: unknown } }): string {
  const command = event.input?.command;
  return typeof command === "string" ? command : "";
}

function filePathOf(event: { input?: { file_path?: unknown; path?: unknown } }): string | undefined {
  const filePath = event.input?.file_path ?? event.input?.path;
  return typeof filePath === "string" ? filePath : undefined;
}
