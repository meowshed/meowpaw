// SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
// SPDX-License-Identifier: Apache-2.0

/**
 * Downloads the platform-specific meow binary from the meowpaw releases.
 *
 * The meow binary is built once for six platforms by the build workflow and
 * published in each unit's release archive. This script downloads it for the
 * current machine and places it at bin/<cpu>-<system>/meow, which is where
 * the shell wrappers look for it.
 */

import { createWriteStream, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { get } from "node:https";
import { platform, arch } from "node:os";
import { chmod } from "node:fs/promises";

const RELEASE_BASE = "https://github.com/meowshed/meowpaw/releases/download";
// Any unit release contains the same meow binary; meow-prose-gate is the one
// the kernel package uses.
const UNIT = "meow-prose-gate";
const VERSION = "0.4.0";

function targetTriple(): string {
  const os = platform();
  const cpu = arch();
  const system = os === "darwin" ? "apple-darwin"
    : os === "linux" ? "unknown-linux-musl"
    : os === "win32" ? "pc-windows-msvc"
    : null;
  const arm = cpu === "arm64" || cpu === "aarch64" ? "aarch64" : "x86_64";
  if (!system) {
    console.warn(`meowpaw: unsupported platform ${os}/${cpu}, skipping binary download`);
    process.exit(0);
  }
  return `${arm}-${system}`;
}

async function download(url: string, dest: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const dir = dirname(dest);
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    const file = createWriteStream(dest);
    const follow = (u: string) => {
      get(u, (res) => {
        if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          follow(res.headers.location);
          return;
        }
        res.pipe(file);
        file.on("finish", () => resolve());
      }).on("error", reject);
    };
    follow(url);
  });
}

async function main() {
  const triple = targetTriple();
  const scriptDir = dirname(new URL(import.meta.url).pathname);
  const binDir = join(scriptDir, "bin", triple);
  const exe = platform() === "win32" ? "meow.exe" : "meow";
  const dest = join(binDir, exe);

  if (existsSync(dest)) {
    process.exit(0);
  }

  const archiveUrl = `${RELEASE_BASE}/${UNIT}-v${VERSION}/${UNIT}-${VERSION}.zip`;
  console.log(`meowpaw: downloading meow binary for ${triple} from ${UNIT} v${VERSION}`);

  // The archive contains bin/<triple>/meow. Download and extract.
  // For simplicity, use the direct binary download if available, otherwise
  // the archive. The release workflow publishes archives; extract with unzip.
  const { execFileSync } = await import("node:child_process");
  const tmp = join(scriptDir, "bin", `.tmp-${triple}.zip`);

  try {
    await download(archiveUrl, tmp);
    mkdirSync(binDir, { recursive: true });
    execFileSync("unzip", ["-jo", tmp, `*/bin/${triple}/meow*`, "-d", binDir], { stdio: "pipe" });
    if (!existsSync(dest)) {
      // Try the .exe variant
      const destExe = join(binDir, "meow.exe");
      if (!existsSync(destExe)) {
        console.warn(`meowpaw: binary not found in archive for ${triple}`);
      }
    }
    if (platform() !== "win32") {
      await chmod(dest, 0o755);
    }
  } finally {
    try { require("node:fs").unlinkSync(tmp); } catch {}
  }
}

main().catch((e) => {
  console.warn(`meowpaw: binary download failed (${e.message}), the shell wrappers will report unrun`);
  process.exit(0);
});
