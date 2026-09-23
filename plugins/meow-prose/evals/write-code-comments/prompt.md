---
name: write-code-comments
description: A writing task where the standard's defects appear without the skill.
tags: [content]
runs: 5
max_turns: 6
---

Add comments to this function where they help a reader, and print the whole function back.

```python
def drain(queue, store):
    count = 0
    while queue:
        batch = queue.pop()
        if not batch.valid():
            continue
        store.write(batch)
        count += 1
    time.sleep(2)
    return count
```

The two-second sleep exists because the store's replication lags by up to two seconds, and a caller reading straight after would miss the last batch.
