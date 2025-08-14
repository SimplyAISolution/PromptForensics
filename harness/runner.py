# harness/runner.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Callable

from Utils.evidence_schema import Evidence, Trace, Artifact
from Utils.detectors import run_all_detectors
from Utils.signals import detect_leakage_signals

def load_cases(cases_dir: str) -> List[Dict[str, Any]]:
    try:
        import yaml
    except Exception as e:
        raise SystemExit("PyYAML required to load YAML cases. Install pyyaml.") from e
    cases = []
    for p in Path(cases_dir).glob("*.yaml"):
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
        if isinstance(data, list):
            cases.extend(data)
    return cases

def run_case(client_invoke: Callable[[str], Dict[str, Any]], case: Dict[str, Any]) -> Evidence:
    payload = ""  # No payload shipped; provide via private provider in real runs
    result = client_invoke(payload)
    ev = Evidence.new(source={"type": "sdk", "path": "runtime"}, provider=result.get("provider"))
    ev.trace = Trace(
        request={"prompt_len": len(payload)},
        response={"text": result.get("text",""), "meta": result.get("meta", {})},
        model=result.get("model"),
        params=result.get("params", {}),
    )
    run_all_detectors(ev)
    sig = detect_leakage_signals(ev.trace.response.get("text",""))
    ev.tags = [k for k,v in sig.items() if v]
    ev.artifacts.append(Artifact(type="signal_summary", data=sig))
    return ev

def write_evidence_jsonl(path: str, evs: List[Evidence]):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ev in evs:
            f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
