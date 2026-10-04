// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw method extension for Pi.
 *
 * Registers the session-start status, the git commit and push guards, the
 * governance guard, the loop guard, the router tool, and a command for each
 * method step and driver. Shells out to the native binary wrappers, which
 * resolve the platform-specific meow binary at runtime.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "typebox";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");
const binDir = join(packageRoot, "bin");

/** Shell out to a binary and interpret its exit code. */
function runBinary(
  binary: string,
  args: string[],
  stdinInput?: string,
  timeout = 30_000,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = execFile(binary, args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
    if (stdinInput !== undefined) {
      child.stdin?.end(stdinInput);
    } else {
      child.stdin?.end();
    }
  });
}

/** Read a file relative to the Claude Code plugins directory. */
async function readPluginFile(plugin: string, ...segments: string[]): Promise<string> {
  const path = join(packageRoot, "..", "..", "plugins", plugin, ...segments);
  try {
    return await readFile(path, "utf-8");
  } catch {
    return "";
  }
}

/** Commands that the git commit guard intercepts. */
const GIT_COMMIT_PATTERN = /\bgit\s+commit\b/;
/** Commands that the git push guard intercepts. */
const GIT_PUSH_PATTERN = /\bgit\s+push\b/;
/** Commands that the governance guard intercepts. */
const GH_GOVERNANCE_PATTERN = /\bgh\s+(?!api\b|auth\b|help\b|version\b)/;

export default function (pi: ExtensionAPI) {
  let replyShape = "";
  let routerPrompt = "";

  // ── Session start ──────────────────────────────────────────────────

  pi.on("session_start", async (_event, _ctx) => {
    // Report what waits at a gate, as meow-flow's SessionStart hook does.
    // Best-effort: swallow errors, the model sees the session regardless.
    await runBinary(join(binDir, "paw"), ["status", "--waiting"]);

    // Load prompt fragments for nested calls.
    replyShape = await readPluginFile("meow-core", "output-styles", "meow.md");
    routerPrompt = await readPluginFile("meow-flow", "agents", "router.md");
  });

  // ── Git commit guard ───────────────────────────────────────────────

  pi.on("user_bash", async (event, _ctx) => {
    const command = typeof event.command === "string" ? event.command : "";
    if (!GIT_COMMIT_PATTERN.test(command)) return undefined;

    const { exitCode, stdout, stderr } = await runBinary(
      join(binDir, "meow-git"), ["commit-guard"],
    );

    if (exitCode === 0) return undefined;

    const reason = stderr.trim() || stdout.trim() || "Commit blocked by meow-git";
    return { result: { content: reason, details: undefined } };
  });

  // ── Git push guard ─────────────────────────────────────────────────

  pi.on("user_bash", async (event, _ctx) => {
    const command = typeof event.command === "string" ? event.command : "";
    if (!GIT_PUSH_PATTERN.test(command)) return undefined;

    const { exitCode, stdout, stderr } = await runBinary(
      join(binDir, "meow-git"), ["push-guard"], undefined, 120_000,
    );

    if (exitCode === 0) return undefined;

    const reason = stderr.trim() || stdout.trim() || "Push blocked by meow-git";
    return { result: { content: reason, details: undefined } };
  });

  // ── GitHub governance guard ────────────────────────────────────────

  pi.on("user_bash", async (event, ctx) => {
    const command = typeof event.command === "string" ? event.command : "";
    if (!GH_GOVERNANCE_PATTERN.test(command)) return undefined;

    const { exitCode, stdout, stderr } = await runBinary(
      join(binDir, "meow-github"), ["governance-guard"],
    );

    if (exitCode === 0) return undefined;

    // The governance guard asks the person. In Pi, prompt via ctx.ui.
    const reason = stderr.trim() || stdout.trim();
    if (ctx.hasUI) {
      const allow = await ctx.ui.confirm(
        `This gh command changes repository governance:\n${reason}\n\nAllow?`,
      );
      if (allow) return undefined;
    }

    return {
      result: {
        content: reason || "Governance change blocked by meow-github",
        details: undefined,
      },
    };
  });

  // ── Loop guard ─────────────────────────────────────────────────────

  pi.on("tool_call", async (event, _ctx) => {
    if (event.toolName !== "bash" && event.toolName !== "edit" && event.toolName !== "write") {
      return undefined;
    }

    const { exitCode, stdout, stderr } = await runBinary(
      join(binDir, "meow-loop"), ["guard"],
    );

    if (exitCode === 0) return undefined;

    const reason = stderr.trim() || stdout.trim() || "Write blocked by meow-loop";
    return { block: true, reason };
  });

  // ── Router tool ────────────────────────────────────────────────────

  pi.registerTool("meow-router", {
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

      const result = await ctx.modelRegistry.streamSimple({
        model: "sonnet",
        messages: [
          { role: "system", content: replyShape },
          { role: "user", content: `${routerPrompt}\n\nRequest: ${args.request}` },
        ],
      });

      return { content: result.text, details: undefined };
    },
  });

  // ── Commands ───────────────────────────────────────────────────────

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
