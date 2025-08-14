# Scaffold PromptForensics/Tools and PromptForensics/Utils with working starter code (stdlib-only).
import os, json, csv, hashlib, re, sys, textwrap, zipfile
from pathlib import Path
from datetime import datetime

root = Path("/mnt/data/PromptForensics-Scaffold")
tools_dir = root / "Tools"
utils_dir = root / "Utils"
parsers_dir = utils_dir / "parsers"
reporters_dir = utils_dir / "reporters"
config_dir = utils_dir / "config"
root.mkdir(parents=True, exist_ok=True)
tools_dir.mkdir(parents=True, exist_ok=True)
utils_dir.mkdir(parents=True, exist_ok=True)
parsers_dir.mkdir(parents=True, exist_ok=True)
reporters_dir.mkdir(parents=True, exist_ok=True)
config_dir.mkdir(parents=True, exist_ok=True)

# ---------------- Utils/evidence_schema.py (dataclasses, stdlib) ----------------
evidence_schema_py = """\
# Utils/evidence_schema.py
# Stdlib-only lightweight schema for evidence records.
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

@dataclass
class Artifact:
    type: str  # 'system_prompt' | 'guardrail' | 'tool_schema' | 'rag_chunk' | 'memory'
    data: Dict[str, Any]
    summary: Optional[str] = None

@dataclass
class Trace:
    request: Dict[str, Any] = field(default_factory=dict)
    response: Dict[str, Any] = field(default_factory=dict)
    model: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Evidence:
    id: str
    timestamp: str
    source: Dict[str, Any]
    provider: Optional[str]
    app: Dict[str, Any]
    trace: Trace
    artifacts: List[Artifact] = field(default_factory=list)
    integrity: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def new(source: Dict[str, Any], provider: Optional[str]=None, app: Optional[Dict[str, Any]]=None) -> "Evidence":
        return Evidence(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            source=source,
            provider=provider,
            app=app or {},
            trace=Trace(),
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # dataclasses asdict already recurses
        return d
"""
# ---------------- Utils/io.py ----------------
utils_io_py = """\
# Utils/io.py
from __future__ import annotations
import json, gzip
from typing import Iterable, Dict, Any, List, Optional
from pathlib import Path

def read_jsonl(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    opener = gzip.open if p.suffix == ".gz" else open
    records = []
    with opener(p, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def write_jsonl(path: str, items: Iterable[Dict[str, Any]]):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "wt", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False) + "\\n")

def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_text(path: str, text: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
"""
# ---------------- Utils/hashing.py ----------------
hashing_py = """\
# Utils/hashing.py
import hashlib, json
from typing import Any

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_obj(obj: Any) -> str:
    # Canonical JSON with sorted keys
    canon = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256_text(canon)
"""
# ---------------- Utils/parsers/har_parser.py ----------------
har_parser_py = """\
# Utils/parsers/har_parser.py
# Minimal HAR parser (stdlib-only). Extracts request/response bodies & basic metadata.
from __future__ import annotations
from typing import Dict, Any, Generator, Optional
from ..hashing import sha256_obj

KNOWN_ENDPOINT_HINTS = [
    "api.openai.com", "anthropic.com", "generativelanguage.googleapis.com",
    "azure.com", "vertexai", "openrouter.ai", "cohere.ai"
]

def provider_from_url(url: str) -> Optional[str]:
    u = url.lower()
    if "openai" in u: return "openai"
    if "anthropic" in u: return "anthropic"
    if "google" in u or "vertex" in u: return "google"
    if "azure" in u: return "azure"
    if "openrouter" in u: return "openrouter"
    if "cohere" in u: return "cohere"
    return None

def iter_llm_entries(har: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    for entry in har.get("log", {}).get("entries", []):
        req = entry.get("request", {})
        res = entry.get("response", {})
        url = req.get("url", "")
        method = req.get("method", "")
        if method not in {"POST", "GET"}:
            continue
        if not any(hint in url for hint in KNOWN_ENDPOINT_HINTS):
            # Not necessarily LLM traffic—still yield if JSON body present
            ctype = None
            for h in req.get("headers", []):
                if h.get("name","").lower() == "content-type":
                    ctype = h.get("value","").lower()
            if not (ctype and "json" in ctype):
                continue
        yield entry

def extract_body(item: Dict[str, Any]) -> Any:
    # HAR stores postData and content in various places
    body = None
    pd = item.get("postData") or {}
    text = pd.get("text")
    if text:
        # attempt JSON; fall back to raw text
        try:
            import json
            body = json.loads(text)
        except Exception:
            body = {"_raw": text}
    return body

def extract_response_content(res: Dict[str, Any]) -> Any:
    content = res.get("content", {})
    text = content.get("text")
    if not text:
        return None
    # Try JSON first
    try:
        import json
        return json.loads(text)
    except Exception:
        return {"_raw": text}

def parse_har(har: Dict[str, Any]):
    for entry in iter_llm_entries(har):
        req = entry.get("request", {})
        res = entry.get("response", {})
        request_body = extract_body(req) if "postData" in req else None
        response_body = extract_response_content(res) or {}
        url = req.get("url","")
        prov = provider_from_url(url)
        model = None
        params = {}
        if isinstance(request_body, dict):
            model = request_body.get("model") or request_body.get("modelId") or None
            params = {k: v for k, v in request_body.items() if k in {"temperature","top_p","top_k","tool_choice","response_format"}}
        yield {
            "provider": prov,
            "url": url,
            "request": request_body or {},
            "response": response_body or {},
            "model": model,
            "params": params,
            "meta": {
                "startedDateTime": entry.get("startedDateTime"),
                "time": entry.get("time"),
            }
        }
"""
# ---------------- Utils/normalizers.py ----------------
normalizers_py = """\
# Utils/normalizers.py
from __future__ import annotations
from typing import Dict, Any, Iterable, List
from .evidence_schema import Evidence, Artifact, Trace

def normalize_trace(item: Dict[str, Any], source_path: str) -> Evidence:
    ev = Evidence.new(source={"type": "har", "path": source_path}, provider=item.get("provider"))
    ev.trace = Trace(
        request=item.get("request", {}),
        response=item.get("response", {}),
        model=item.get("model"),
        params=item.get("params", {}),
    )
    # Best-effort app metadata
    ev.app = {"name": "unknown", "version": None}
    return ev
"""
# ---------------- Utils/detectors.py ----------------
detectors_py = """\
# Utils/detectors.py
from __future__ import annotations
from typing import List
from .evidence_schema import Evidence, Artifact
from .hashing import sha256_text

def detect_system_prompts(ev: Evidence) -> List[Artifact]:
    found = []
    # Look in response structures commonly used by LLM providers
    resp = ev.trace.response or {}
    # OpenAI-ish
    for choice in (resp.get("choices") or []):
        msg = (choice.get("message") or {})
        role = msg.get("role")
        if role == "system":
            text = msg.get("content") or ""
            found.append(Artifact(type="system_prompt", data={"text": text, "hash": sha256_text(text)}))
    # Anthropic-ish
    for content in (resp.get("content") or []):
        if isinstance(content, dict) and content.get("type") == "system":
            text = content.get("text") or ""
            found.append(Artifact(type="system_prompt", data={"text": text, "hash": sha256_text(text)}))
    return found

def detect_tool_schemas(ev: Evidence) -> List[Artifact]:
    found = []
    req = ev.trace.request or {}
    tools = req.get("tools") or req.get("functions") or []
    if isinstance(tools, list) and tools:
        for t in tools:
            if isinstance(t, dict):
                name = t.get("name") or t.get("function",{}).get("name")
                params = t.get("parameters") or t.get("function",{}).get("parameters")
                found.append(Artifact(type="tool_schema", data={"name": name, "jsonschema": params}))
    return found

def detect_guardrails(ev: Evidence) -> List[Artifact]:
    found = []
    # Heuristics: look for safety/moderation fields in request or response
    for src in (ev.trace.request, ev.trace.response):
        if not isinstance(src, dict):
            continue
        if "safety_settings" in src or "moderation" in src or "guardrail" in src:
            found.append(Artifact(type="guardrail", data={"raw": src.get("safety_settings") or src.get("moderation") or src.get("guardrail")}))
    return found

def run_all_detectors(ev: Evidence) -> Evidence:
    ev.artifacts.extend(detect_system_prompts(ev))
    ev.artifacts.extend(detect_tool_schemas(ev))
    ev.artifacts.extend(detect_guardrails(ev))
    return ev
"""
# ---------------- Utils/reporters/markdown_reporter.py ----------------
md_reporter_py = """\
# Utils/reporters/markdown_reporter.py
from __future__ import annotations
from typing import List, Dict, Any
from ..evidence_schema import Evidence

def summarize_artifact(a: Dict[str, Any]) -> str:
    t = a.get("type")
    d = a.get("data", {})
    if t == "system_prompt":
        text = (d.get("text") or "")[:120].replace("\\n", " ")
        return f"{len(d.get('text',''))} chars. Preview: {text!r}…"
    if t == "tool_schema":
        name = d.get("name")
        return f"Tool {name} with JSONSchema params"
    if t == "guardrail":
        return "Safety/guardrail configuration present"
    return "—"

def to_markdown(evidence: List[Evidence]) -> str:
    lines = ["# PromptForensics Report", ""]
    for ev in evidence:
        lines.append(f"## Evidence {ev.id}")
        lines.append(f"- Timestamp: {ev.timestamp}")
        lines.append(f"- Provider: {ev.provider or 'unknown'}")
        lines.append(f"- Model: {ev.trace.model or 'unknown'}")
        lines.append("")
        lines.append("| Artifact | Summary |")
        lines.append("|---|---|")
        for art in ev.artifacts:
            lines.append(f"| {art.type} | {summarize_artifact({'type': art.type, 'data': art.data})} |")
        lines.append("")
    return "\\n".join(lines)
"""
# ---------------- Utils/reporters/csv_reporter.py ----------------
csv_reporter_py = """\
# Utils/reporters/csv_reporter.py
from __future__ import annotations
from typing import List
import csv
from ..evidence_schema import Evidence

def write_csv(path: str, evidence: List[Evidence]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["evidence_id","timestamp","provider","model","artifact_type","artifact_summary"])
        for ev in evidence:
            for a in ev.artifacts:
                if a.type == "system_prompt":
                    text = (a.data.get("text") or "")
                    summary = f"{len(text)} chars"
                elif a.type == "tool_schema":
                    summary = f"tool={a.data.get('name')}"
                elif a.type == "guardrail":
                    summary = "guardrail present"
                else:
                    summary = ""
                w.writerow([ev.id, ev.timestamp, ev.provider or "", ev.trace.model or "", a.type, summary])
"""
# ---------------- Utils/config/default_rules.yaml ----------------
default_rules_yaml = """\
# Utils/config/default_rules.yaml
detectors:
  - name: system_prompt_block
    match:
      any:
        - path: $.trace.response.choices[*].message.role == "system"
        - path: $.trace.response.content[?(@.type=="system")]
    actions: [capture_text, hash]
  - name: guardrail_fields
    match:
      any:
        - path: $.trace.request.safety_settings
        - path: $.trace.response.moderation
    actions: [capture_raw]
"""

# ---------------- Tools/har_extract.py ----------------
har_extract_py = """\
#!/usr/bin/env python3
# Tools/har_extract.py
from __future__ import annotations
import argparse, json
from pathlib import Path
from Utils.parsers.har_parser import parse_har
from Utils.normalizers import normalize_trace
from Utils.detectors import run_all_detectors
from Utils.io import write_jsonl

def main():
    ap = argparse.ArgumentParser(description="Extract prompts/tools/guardrails from HAR")
    ap.add_argument("--in", dest="in_path", required=True, help="Input HAR file")
    ap.add_argument("--out", dest="out_path", required=True, help="Output JSONL evidence")
    args = ap.parse_args()

    har = json.loads(Path(args.in_path).read_text(encoding="utf-8"))
    items = []
    for item in parse_har(har):
        ev = normalize_trace(item, source_path=args.in_path)
        ev = run_all_detectors(ev)
        items.append(ev.to_dict())

    write_jsonl(args.out_path, items)
    print(f"[ok] wrote {len(items)} evidence records -> {args.out_path}")

if __name__ == "__main__":
    main()
"""

# ---------------- Tools/report_generate.py ----------------
report_generate_py = """\
#!/usr/bin/env python3
# Tools/report_generate.py
from __future__ import annotations
import argparse, json
from pathlib import Path
from Utils.io import read_jsonl, write_text
from Utils.evidence_schema import Evidence, Artifact, Trace
from Utils.reporters.markdown_reporter import to_markdown
from Utils.reporters.csv_reporter import write_csv as write_csv_report

def load_evidence(path: str):
    records = read_jsonl(path)
    evs = []
    for r in records:
        tr = r.get("trace", {})
        e = Evidence(
            id=r.get("id"),
            timestamp=r.get("timestamp"),
            source=r.get("source", {}),
            provider=r.get("provider"),
            app=r.get("app", {}),
            trace=Trace(
                request=tr.get("request", {}),
                response=tr.get("response", {}),
                model=tr.get("model"),
                params=tr.get("params", {}),
            ),
            artifacts=[Artifact(type=a.get("type"), data=a.get("data"), summary=a.get("summary")) for a in r.get("artifacts", [])],
            integrity=r.get("integrity", {}),
            tags=r.get("tags", []),
        )
        evs.append(e)
    return evs

def main():
    ap = argparse.ArgumentParser(description="Generate MD/CSV reports from evidence JSONL")
    ap.add_argument("--in", dest="in_path", required=True)
    ap.add_argument("--out", dest="out_path", required=True, help="Output file (.md or .csv)")
    args = ap.parse_args()

    evs = load_evidence(args.in_path)
    out = args.out_path
    if out.lower().endswith(".md"):
        md = to_markdown(evs)
        write_text(out, md)
        print(f"[ok] wrote markdown report -> {out}")
    elif out.lower().endswith(".csv"):
        write_csv_report(out, evs)
        print(f"[ok] wrote csv report -> {out}")
    else:
        raise SystemExit("Output must end with .md or .csv")

if __name__ == "__main__":
    main()
"""

# ---------------- Tools/prompt_diff.py ----------------
prompt_diff_py = """\
#!/usr/bin/env python3
# Tools/prompt_diff.py
from __future__ import annotations
import argparse
from Utils.io import read_jsonl, write_text

def extract_prompts(records):
    prompts = []
    for r in records:
        for a in r.get("artifacts", []):
            if a.get("type") == "system_prompt":
                h = (a.get("data") or {}).get("hash")
                t = (a.get("data") or {}).get("text","")
                prompts.append((h,t))
    return prompts

def main():
    ap = argparse.ArgumentParser(description="Diff two evidence sets for prompt drift")
    ap.add_argument("--a", required=True, help="Evidence JSONL A")
    ap.add_argument("--b", required=True, help="Evidence JSONL B")
    ap.add_argument("--out", required=True, help="Markdown diff output")
    args = ap.parse_args()

    A = read_jsonl(args.a); B = read_jsonl(args.b)
    a_prompts = {h for h,_ in extract_prompts(A) if h}
    b_prompts = {h for h,_ in extract_prompts(B) if h}

    added = b_prompts - a_prompts
    removed = a_prompts - b_prompts
    unchanged = a_prompts & b_prompts

    lines = ["# Prompt Diff", "", "## Added", *[f"- {h}" for h in sorted(added)] or ["- (none)"], "", "## Removed", *[f"- {h}" for h in sorted(removed)] or ["- (none)"], "", "## Unchanged", *[f"- {h}" for h in sorted(unchanged)] or ["- (none)"]]
    write_text(args.out, "\\n".join(lines))
    print(f"[ok] wrote diff -> {args.out}")

if __name__ == "__main__":
    main()
"""

# ---------------- Tools/sdk_normalize.py ----------------
sdk_normalize_py = """\
#!/usr/bin/env python3
# Tools/sdk_normalize.py
from __future__ import annotations
import argparse, json
from Utils.normalizers import normalize_trace
from Utils.detectors import run_all_detectors
from Utils.io import write_jsonl

def main():
    ap = argparse.ArgumentParser(description="Normalize SDK logs to common evidence JSONL")
    ap.add_argument("--in", dest="in_path", required=True, help="Input JSON/JSONL of SDK traces")
    ap.add_argument("--out", dest="out_path", required=True, help="Output JSONL evidence")
    args = ap.parse_args()

    # Accept JSON array or JSONL
    items = []
    try:
        raw = json.loads(open(args.in_path, "r", encoding="utf-8").read())
        if isinstance(raw, list):
            src = raw
        else:
            src = raw.get("traces") or []
    except Exception:
        # Try JSONL
        src = [json.loads(line) for line in open(args.in_path, "r", encoding="utf-8") if line.strip()]

    records = []
    for it in src:
        # Expect keys: provider/url/request/response/model/params (best-effort)
        item = {
            "provider": it.get("provider"),
            "url": it.get("url"),
            "request": it.get("request") or {},
            "response": it.get("response") or {},
            "model": it.get("model"),
            "params": it.get("params") or {},
        }
        ev = normalize_trace(item, source_path=args.in_path)
        ev = run_all_detectors(ev)
        records.append(ev.to_dict())

    write_jsonl(args.out_path, records)
    print(f"[ok] wrote {len(records)} evidence records -> {args.out_path}")

if __name__ == "__main__":
    main()
"""

# Write files
(files := {
    utils_dir / "evidence_schema.py": evidence_schema_py,
    utils_dir / "io.py": utils_io_py,
    utils_dir / "hashing.py": hashing_py,
    utils_dir / "normalizers.py": normalizers_py,
    utils_dir / "detectors.py": detectors_py,
    parsers_dir / "har_parser.py": har_parser_py,
    reporters_dir / "markdown_reporter.py": md_reporter_py,
    reporters_dir / "csv_reporter.py": csv_reporter_py,
    config_dir / "default_rules.yaml": default_rules_yaml,
    tools_dir / "har_extract.py": har_extract_py,
    tools_dir / "report_generate.py": report_generate_py,
    tools_dir / "prompt_diff.py": prompt_diff_py,
    tools_dir / "sdk_normalize.py": sdk_normalize_py,
}).items()

for path, content in files:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Make an index README in the scaffold root that points to main README previously generated
index_md = """\
# PromptForensics Scaffold
This archive contains `Tools/` and `Utils/` starter modules referenced by your main README.
"""
(root / "README-SCAFFOLD.md").write_text(index_md, encoding="utf-8")

# Zip it up for easy download
zip_path = "/mnt/data/PromptForensics-Tools-Utils.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob("*"):
        z.write(p, p.relative_to(root))

# Return a simple directory listing and zip path
dir_listing = []
for p in root.rglob("*"):
    dir_listing.append(str(p.relative_to(root)))
{"zip_path": zip_path, "tree": dir_listing[:200]}
