# Utils/signals.py
from __future__ import annotations
import re
from typing import Dict

SYSTEM_TERMS = [r"\bsystem prompt\b", r"\brole:\s*system\b", r"\binternal (policy|instructions?)\b", r"\bdeveloper (prompt|instructions?)\b", r"\b(hidden|secret)\s+(prompt|context)\b"]
TOOL_TERMS = [r"\b(function|tool)(_|\s*)(name|schema|parameters?)\b", r"\bjsonschema\b", r"\btool[_\s]*choice\b"]

def detect_leakage_signals(text: str) -> Dict[str, bool]:
    low = text.lower()
    def any_match(patterns):
        return any(re.search(p, low, re.I) for p in patterns)
    return {"mentions_system": any_match(SYSTEM_TERMS), "mentions_tool_schema": any_match(TOOL_TERMS)}
