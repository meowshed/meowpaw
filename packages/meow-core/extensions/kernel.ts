// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * meowpaw kernel extension for Pi.
 *
 * This is the one extension that injects the reply shape into the system
 * prompt, and the one that puts the meow binary on PATH: the binary ships
 * with this package alone, and every other meowpaw package's launcher
 * falls back to it (REQ-4144, ADR-2810).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(__dirname, "..");
const binDir = join(packageRoot, "bin");
const promptsDir = join(packageRoot, "prompts");

async function readPrompt(name: string): Promise<string> {
  try {
    return await readFile(join(promptsDir, name), "utf-8");
  } catch {
    return "";
  }
}

export default async function (pi: ExtensionAPI) {
  const triple = `${process.arch === "arm64" || process.arch === "aarch64" ? "aarch64" : "x86_64"}-${
    process.platform === "darwin" ? "apple-darwin"
    : process.platform === "linux" ? "unknown-linux-musl"
    : process.platform === "win32" ? "pc-windows-msvc"
    : "unknown"}`;
  process.env.PATH = `${join(binDir, triple)}:${process.env.PATH ?? ""}`;

  // Load the bundled reply shape in the factory, so the first request
  // already holds it: print mode fires no session_start before its request.
  const replyShape = await readPrompt("reply-shape.md");

  if (!replyShape) {
    pi.on("session_start", (_event, ctx) => {
      ctx.ui?.notify?.(
        "meow-core: prompts/reply-shape.md is missing, so the reply shape was not injected",
        "warning",
      );
    });
  }

  pi.on("before_agent_start", async (event, _ctx) => {
    if (replyShape) {
      event.systemPromptOptions.promptGuidelines.push(replyShape);
    }
  });
}