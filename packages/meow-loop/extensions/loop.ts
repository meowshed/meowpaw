// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-loop extension for Pi.
 *
 * Holds a run inside its own step and its own state: a run starts from the
 * session through the runner's `prompt` subcommand (REQ-4616), every other
 * submitted input reaches the same subcommand so the person's next prompt
 * ends the run `cancelled`, the settle boundary asks the runner's `stop`
 * subcommand and continues once with the frozen prompt it names, and the
 * guards deny the Bash command that would start a run and the write that
 * would touch a run's files (SPC-1300).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");

function runRunner(
  args: string[],
  event: object,
  timeout: number,
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const child = execFile(join(binDir, "meow-loop"), args, { timeout }, (error, stdout, stderr) => {
      resolve({
        exitCode: error ? (error as NodeJS.ErrnoException & { code?: number }).code ?? 1 : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
    child.stdin?.end(JSON.stringify(event));
  });
}

/** The permission decision a guard printed, or undefined where it stayed silent. */
function decision(stdout: string): { decision: string; reason: string } | undefined {
  const match = stdout.match(/"permissionDecision":\s*"(ask|deny)"/);
  if (!match) return undefined;
  const reason = stdout.match(/"permissionDecisionReason":\s*"((?:[^"\\]|\\.)*)"/);
  return { decision: match[1], reason: reason?.[1]?.replace(/\\n/g, "\n") ?? "" };
}

/** The JSON the runner's subcommands answer with, or its plain text. */
function said(stdout: string): {
  systemMessage?: string;
  additionalContext?: string;
  decision?: string;
  reason?: string;
} {
  try {
    return JSON.parse(stdout.trim());
  } catch {
    return { systemMessage: stdout.trim() || undefined };
  }
}

function filePathOf(event: { input?: { file_path?: unknown; path?: unknown } }): string | undefined {
  const filePath = event.input?.file_path ?? event.input?.path;
  return typeof filePath === "string" ? filePath : undefined;
}

export default async function (pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;

  const sessionId = (ctx: { sessionManager?: { getSessionId?: () => string } }) =>
    ctx.sessionManager?.getSessionId?.() ?? "";

  // The person starts a run by typing the command (REQ-0894): the runner's
  // `prompt` subcommand writes the run's files and names the first
  // iteration, which goes into the session as a user message.
  pi.registerCommand("meow-loop:run", {
    description:
      "Start a run in this session: it repeats the method's chain until the record holds no open work or a bound is reached",
    handler: async (args, ctx) => {
      const prompt = `/meow-loop:run${args ? ` ${args}` : ""}`;
      const { stdout } = await runRunner(
        ["prompt"],
        {
          hook_event_name: "UserPromptSubmit",
          prompt,
          session_id: sessionId(ctx),
          cwd: ctx.cwd,
        },
        30_000,
      );
      const answer = said(stdout);
      if (answer.additionalContext) {
        if (answer.systemMessage && ctx.hasUI) ctx.ui.notify(answer.systemMessage, "info");
        pi.sendUserMessage(answer.additionalContext);
        return;
      }
      if (ctx.hasUI) {
        ctx.ui.notify(answer.systemMessage ?? "meow-loop: the runner answered nothing", "warning");
      }
    },
  });

  // Any other submitted input reaches the runner, so the person's next
  // prompt ends an active run `cancelled` the way the hook does on Claude
  // Code. The extension's own messages never reach it, or a run's first
  // context would cancel the run it started.
  pi.on("input", async (event, ctx) => {
    if (event.source === "extension") return { action: "continue" };
    await runRunner(
      ["prompt"],
      {
        hook_event_name: "UserPromptSubmit",
        prompt: event.text,
        session_id: sessionId(ctx),
        cwd: ctx.cwd,
      },
      30_000,
    );
    return { action: "continue" };
  });

  // The settle boundary is where the Stop hook decides on Claude Code: the
  // runner logs the iteration, and its `block` answer carries the frozen
  // prompt, which goes in as one message and continues the session once.
  pi.on("agent_before_settle", async (event, ctx) => {
    if (event.outcome === "aborted") return undefined;
    const { stdout } = await runRunner(
      ["stop"],
      {
        hook_event_name: "Stop",
        session_id: sessionId(ctx),
        cwd: ctx.cwd,
        stop_hook_active: true,
      },
      60_000,
    );
    const answer = said(stdout);
    if (answer.decision === "block" && answer.reason) {
      return {
        entries: [
          { type: "custom_message", customType: "meow-loop-run", content: answer.reason, display: true },
        ],
        continue: true,
      };
    }
    if (answer.systemMessage && ctx.hasUI) ctx.ui.notify(answer.systemMessage, "info");
    return undefined;
  });

  pi.on("tool_call", async (event, _ctx) => {
    let reason: string | undefined;

    if (event.toolName === "bash") {
      const command = typeof event.input?.command === "string" ? event.input.command : "";
      const { stdout } = await runRunner(
        ["guard"],
        { tool_name: "Bash", tool_input: { command } }, 10_000,
      );
      const denied = decision(stdout);
      if (denied?.decision === "deny") reason = denied.reason;
    } else if (event.toolName === "edit" || event.toolName === "write") {
      const filePath = filePathOf(event);
      if (filePath !== undefined) {
        const { stdout } = await runRunner(
          ["guard"],
          { tool_name: event.toolName, tool_input: { file_path: filePath } }, 10_000,
        );
        const denied = decision(stdout);
        if (denied?.decision === "deny") reason = denied.reason;
      }
    }

    if (reason === undefined) return undefined;
    return { block: true, reason };
  });

  pi.on("user_bash", async (event, _ctx) => {
    const { stdout } = await runRunner(
      ["guard"],
      { tool_name: "Bash", tool_input: { command: event.command } }, 10_000,
    );
    const denied = decision(stdout);
    if (denied?.decision !== "deny") return undefined;
    return {
      result: { output: denied.reason, exitCode: 126, cancelled: false, truncated: false },
    };
  });
}