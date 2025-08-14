# Test Case Metadata

This directory holds **metadata-only** YAML files. **No payloads** are stored here.

- Teams provide payloads privately at runtime (vault/secret store), keyed by `id`.
- The harness reads the metadata to determine **objectives** and **success signals**.
- Responses are analyzed for **signals** (keywords/regex) — see `Utils/signals.py`.
