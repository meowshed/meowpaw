// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * Pi extension for this unit.
 *
 * Puts the package's launcher on PATH so the skills call it by name, the
 * way Claude Code does natively for a plugin's bin/. The meow binary comes
 * from the core package's install (REQ-4144).
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const binDir = join(__dirname, "..", "bin");

export default function (_pi: ExtensionAPI) {
  process.env.PATH = `${binDir}:${process.env.PATH ?? ""}`;
}
