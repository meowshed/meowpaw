---
name: write-howto-steps
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Write the steps an operator follows to rotate the importer's database password. The new password goes into the secrets store first; restarting the importer before that makes it fail to connect and drop the batch in flight. If the importer runs on more than one host, every host restarts. Print only the steps.
