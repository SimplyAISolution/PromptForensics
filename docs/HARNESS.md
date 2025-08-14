# Safe Test Harness (Skeleton)

This harness is designed for **authorized**, **policy-compliant** LLM security testing.
It **does not** ship jailbreak payloads or evasion strings. Teams supply payloads privately
under scope & authorization.

```mermaid
flowchart LR
  A[Test Case Metadata (YAML)] --> B[run_harness.py]
  B --> C[Authorized Target Adapter]
  C --> D[Response]
  D --> E[PromptForensics Normalizer & Detectors]
  E --> F[Signals & Scoring]
  F --> G[Reports]
```

**Gates**
- `SCOPE_TOKEN` secret must be present (CI or local env).
- Target must be in `config/allowlist.json`.

**Run (local)**
```bash
python Tools/run_harness.py --target sandbox-target \
  --cases-dir tests/cases \
  --out data/evidence/harness.jsonl
```
Then generate reports:
```bash
python Tools/report_generate.py --in data/evidence/harness.jsonl --out reports/harness.md
```

**Implement a provider adapter**
Edit `get_client_adapter()` in `Tools/run_harness.py` to call your LLM API in authorized environments.
