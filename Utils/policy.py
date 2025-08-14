# Utils/policy.py
from __future__ import annotations
import os, json
from pathlib import Path
from typing import Set

def load_allowlist(path: str) -> Set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return set(data.get("allowed_targets", []))
    except Exception:
        return set()

def authorized(scope_token_env: str, target: str, allowlist_path: str) -> bool:
    token = os.environ.get(scope_token_env, "").strip()
    if not token:
        return False
    allow = load_allowlist(allowlist_path)
    return target in allow
