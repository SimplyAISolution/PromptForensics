#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from Tools.cli_utils import (
    build_parser, add_verbosity_args, add_common_flags, print_banner,
    cprint, FG_GREEN, FG_RED, set_log_level, get_logger, validate_io_args, add_io_args
)
from Utils.policy import authorized
from harness.runner import load_cases, run_case, write_evidence_jsonl

def get_client_adapter(target: str):
    def _invoke(_payload: str):
        text = f"Stub response for target={target}; integrate your provider adapter."
        return {"text": text, "model": "unknown", "meta": {"target": target}, "provider": None, "params": {}}
    return _invoke

def main():
    parser = build_parser("PromptForensics Safe Harness Runner (no payloads shipped)")
    parser.add_argument("--target", required=True, help="Logical target name (must be allowlisted).")
    parser.add_argument("--cases-dir", default="tests/cases", help="Directory with YAML test case metadata.")
    parser.add_argument("--allowlist", default="config/allowlist.json", help="JSON allowlist file.")
    parser.add_argument("--scope-env", default="SCOPE_TOKEN", help="Env var name holding scope token.")
    add_io_args(parser, need_in=False, need_out=True, out_help="Evidence JSONL output path")
    add_verbosity_args(parser)
    add_common_flags(parser)
    args = parser.parse_args()

    set_log_level(args.verbose)
    log = get_logger("run_harness")
    validate_io_args(args, must_exist_in=False, create_out_dirs=True)

    print_banner("PromptForensics • Safe Harness", version="0.1.0")
    if not authorized(args.scope_env, args.target, args.allowlist):
        cprint("[denied] Missing/invalid scope or target not allowlisted.", color=FG_RED, bold=True)
        return sys.exit(5)

    try:
        cases = load_cases(args.cases_dir)
    except Exception as e:
        log.warning("Failed to load YAML cases from %s: %s", args.cases_dir, e)
        cases = []

    client_invoke = get_client_adapter(args.target)
    evidence = []
    for case in cases or [{"id": "NO-CASES", "category": "none", "objective": "skeleton"}]:
        ev = run_case(client_invoke, case)
        evidence.append(ev)

    write_evidence_jsonl(args.out_path, evidence)
    cprint(f"[ok] wrote {len(evidence)} evidence records -> {args.out_path}", color=FG_GREEN, bold=True)

if __name__ == "__main__":
    main()
