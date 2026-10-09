#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Keep the released `marketplace.json` free of relative sources (REQ-1485, BUG-1520).

The platform reads the served file as a `url` marketplace, so it has no
`plugins/` directory to resolve `./plugins/<unit>` against and refuses each such
entry. A run for one unit's tag packs that unit alone, so `fill` takes the
other units' archive entries from the file already published, and `check`
fails the run, naming each unit that is still relative, before it publishes.

    python3 tools/marketplace_release.py fill FILE PREVIOUS
    python3 tools/marketplace_release.py check FILE
"""

import json
import sys
from pathlib import Path


def relative_entries(doc):
    """Names of the entries whose `source` is a path string and not an archive object."""
    return [p["name"] for p in doc.get("plugins", []) if isinstance(p.get("source"), str)]


def fill(doc, previous):
    """Return `doc` with each relative entry replaced by the same unit's archive entry in `previous`."""
    published = {p["name"]: p for p in (previous or {}).get("plugins", []) if isinstance(p.get("source"), dict)}
    plugins = [published.get(p["name"], p) if isinstance(p.get("source"), str) else p for p in doc["plugins"]]
    return {**doc, "plugins": plugins}


def main(argv):
    if len(argv) == 2 and argv[0] == "check":
        left = relative_entries(json.loads(Path(argv[1]).read_text()))
        for name in left:
            print(f"{argv[1]}: {name} has a relative source, which the platform refuses from a served file")
        return 1 if left else 0
    if len(argv) == 3 and argv[0] == "fill":
        path, previous = Path(argv[1]), Path(argv[2])
        doc = json.loads(path.read_text())
        path.write_text(json.dumps(fill(doc, json.loads(previous.read_text()) if previous.is_file() else None), indent=2) + "\n")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
