"""
cli_utils.py — Shared helpers for PromptForensics CLI tools (stdlib-only).

Purpose
-------
Provide consistent argument parsing, terminal output, path validation,
and logging utilities for scripts under `Tools/`.

Import
------
    from Tools.cli_utils import (
        build_parser, add_io_args, add_verbosity_args,
        validate_io_args, print_banner, cprint, Stopwatch,
        set_log_level, get_logger, die, format_kv_table,
        FG_RED, FG_GREEN, FG_YELLOW, FG_CYAN
    )
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import shutil
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Iterable, Optional, Tuple

# --------------------------- Color & Printing ---------------------------

def _isatty(stream) -> bool:
    try:
        return hasattr(stream, "isatty") and stream.isatty()
    except Exception:
        return False

def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return _isatty(sys.stdout)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"

def _wrap(color: str, text: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{RESET}"

def cprint(text: str, *, color: Optional[str]=None, file=None, bold: bool=False) -> None:
    """Color-aware print. Use like: cprint('ok', color=FG_GREEN)."""
    file = file or sys.stdout
    if bold:
        text = f"{BOLD}{text}{RESET}" if _supports_color() else text
    if color:
        text = _wrap(color, text)
    print(text, file=file)

def print_banner(title: str, *, version: Optional[str]=None) -> None:
    cols = shutil.get_terminal_size((80, 20)).columns
    line = "─" * max(10, min(cols - 2, 100))
    title_line = f"{title}"
    if version:
        title_line += f"  v{version}"
    if _supports_color():
        line = _wrap(FG_CYAN, line)
        title_line = _wrap(BOLD, title_line)
    print(line)
    print(title_line)
    print(line)

# --------------------------- Logging Helpers ---------------------------

_LOG_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
    3: logging.NOTSET,  # ultra-verbose
}

def set_log_level(verbosity: int = 0) -> None:
    level = _LOG_LEVELS.get(max(0, min(int(verbosity), 3)), logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "PromptForensics")

# --------------------------- Parser Builders ---------------------------

def build_parser(description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=description)

def add_io_args(
    parser: argparse.ArgumentParser,
    *,
    need_in: bool = True,
    need_out: bool = True,
    in_help: str = "Input file path",
    out_help: str = "Output file path",
) -> None:
    if need_in:
        parser.add_argument("--in", dest="in_path", required=True, help=in_help)
    if need_out:
        parser.add_argument("--out", dest="out_path", required=True, help=out_help)
    parser.add_argument("--force", action="store_true",
                        help="Overwrite output if it exists without prompt.")

def add_verbosity_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity (-v, -vv, -vvv).")

def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true", help="Run without writing outputs.")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output.")

# --------------------------- Path Validation ---------------------------

@dataclass
class IOArgs:
    in_path: Optional[Path] = None
    out_path: Optional[Path] = None
    force: bool = False

def validate_io_args(
    args,
    *,
    must_exist_in: bool = True,
    create_out_dirs: bool = True
) -> IOArgs:
    """Validate --in/--out, create parent dirs if requested, and guard overwrites."""
    in_p = Path(getattr(args, "in_path", "")) if hasattr(args, "in_path") and getattr(args, "in_path") else None
    out_p = Path(getattr(args, "out_path", "")) if hasattr(args, "out_path") and getattr(args, "out_path") else None
    force = bool(getattr(args, "force", False))

    if in_p:
        if must_exist_in and not in_p.exists():
            cprint(f"[error] Input not found: {in_p}", color=FG_RED, bold=True, file=sys.stderr)
            sys.exit(2)
        if in_p.exists() and in_p.is_dir():
            cprint(f"[error] Input path is a directory, expected file: {in_p}", color=FG_RED, bold=True, file=sys.stderr)
            sys.exit(2)

    if out_p:
        parent = out_p.parent
        if create_out_dirs:
            parent.mkdir(parents=True, exist_ok=True)
        if out_p.exists() and not force:
            cprint(f"[error] Output exists (use --force to overwrite): {out_p}", color=FG_RED, bold=True, file=sys.stderr)
            sys.exit(3)

    return IOArgs(in_path=in_p, out_path=out_p, force=force)

# --------------------------- Timing ---------------------------

class Stopwatch:
    """Simple stopwatch for measuring steps in CLI tools."""
    def __init__(self):
        self._t0 = None
        self.elapsed = 0.0

    def start(self):
        self._t0 = perf_counter()
        return self

    def stop(self) -> float:
        if self._t0 is None:
            return 0.0
        self.elapsed = perf_counter() - self._t0
        self._t0 = None
        return self.elapsed

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, tb):
        self.stop()

# --------------------------- Formatting ---------------------------

def format_kv_table(rows: Iterable[Tuple[str, str]]) -> str:
    """Return a simple left-aligned key/value table as a string."""
    rows = list(rows)
    if not rows:
        return ""
    key_w = max(len(k) for k, _ in rows)
    lines = []
    for k, v in rows:
        lines.append(f"{k.ljust(key_w)} : {v}")
    return "\n".join(lines)

# --------------------------- Exit Helpers ---------------------------

def die(msg: str, code: int = 1) -> None:
    cprint(msg, color=FG_RED, bold=True, file=sys.stderr)
    sys.exit(code)
