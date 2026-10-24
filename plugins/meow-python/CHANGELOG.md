# meow-python

## 0.1.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.1.0

- First release: `status`, `bind` and `check` for Python projects, detected from `pyproject.toml`, with every tool run through the environment tool the project declares and each tool's cache kept out of the working tree.
