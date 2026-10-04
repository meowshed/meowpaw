// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meow-git extension for Pi.
 *
 * Holds the commit and push guards over every git command the model runs,
 * relaying the guard binary's verdict (SPC-1300).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");
// The scm launcher lives in the sibling meow-scm package, and the git
// binary looks for it beside itself or at MEOW_SCM (REQ-4144).
const scmLauncher = join(__dirname, "..", "..", "meow-scm", "bin", "meow-scm");

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

const GIT_COMMIT_PATTERN = /\bgit\s+commit\b/;
const GIT_PUSH_PATTERN = /\bgit\s+push\b/;

export default async function (pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;
  if (existsSync(scmLauncher)) {
    process.env.MEOW_SCM = scmLauncher;
  }

  pi.on("tool_call", async (event, _ctx) => {
    if (event.toolName !== "bash") return undefined;

    const command = typeof event.input?.command === "string" ? event.input.command : "";
    let reason: string | undefined;

    if (GIT_COMMIT_PATTERN.test(command)) {
      const { exitCode, stderr, stdout } = await runGuard(
        join(binDir, "meow-git"), ["commit-guard"],
        { tool_name: "Bash", tool_input: { command } }, 30_000,
      );
      if (exitCode !== 0) {
        reason = stderr.trim() || stdout.trim() || "Commit blocked by meow-git";
      }
    }

    if (reason === undefined && GIT_PUSH_PATTERN.test(command)) {
      const { exitCode, stderr, stdout } = await runGuard(
        join(binDir, "meow-git"), ["push-guard"],
        { tool_name: "Bash", tool_input: { command } }, 120_000,
      );
      if (exitCode !== 0) {
        reason = stderr.trim() || stdout.trim() || "Push blocked by meow-git";
      }
    }

    if (reason === undefined) return undefined;
    return { block: true, reason };
  });

  // A command the person types with ! in front of it.
  pi.on("user_bash", async (event, _ctx) => {
    let reason: string | undefined;

    if (GIT_COMMIT_PATTERN.test(event.command)) {
      const { exitCode, stderr, stdout } = await runGuard(
        join(binDir, "meow-git"), ["commit-guard"],
        { tool_name: "Bash", tool_input: { command: event.command } }, 30_000,
      );
      if (exitCode !== 0) {
        reason = stderr.trim() || stdout.trim() || "Commit blocked by meow-git";
      }
    }

    if (reason === undefined && GIT_PUSH_PATTERN.test(event.command)) {
      const { exitCode, stderr, stdout } = await runGuard(
        join(binDir, "meow-git"), ["push-guard"],
        { tool_name: "Bash", tool_input: { command: event.command } }, 120_000,
      );
      if (exitCode !== 0) {
        reason = stderr.trim() || stdout.trim() || "Push blocked by meow-git";
      }
    }

    if (reason === undefined) return undefined;
    return {
      result: { output: reason, exitCode: 126, cancelled: false, truncated: false },
    };
  });
}