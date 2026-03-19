"""
core/log_analyzer.py
---------------------
Reads log files and extracts level statistics.
Concepts: generators (yield), re regex, collections.Counter,
          list comprehensions, file handling
"""

import re
import logging
from collections import Counter
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)

# Compile once — reusing a compiled pattern is faster than
# re.search(pattern_string, line) inside a loop every iteration
LOG_PATTERN = re.compile(r"\b(ERROR|WARNING|INFO|DEBUG)\b")


# ── Generator ──────────────────────────────────────────────────────────────────

def stream_log_lines(log_path: str) -> Generator[str, None, None]:
    """
    Generator that yields one log line at a time.
    Memory-efficient — never loads the whole file into RAM.

    Generator[str, None, None] means:
        yields str, receives nothing via send(), returns nothing
    """
    path = Path(log_path)

    if not path.exists():
        logger.warning(f"Log file not found: {log_path}")
        return   # stops the generator immediately — yields nothing

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            yield line.rstrip()   # yield one line, strip trailing whitespace


# ── Analyzer ───────────────────────────────────────────────────────────────────

def analyze_logs(log_path: str) -> dict:
    """
    Scan log file and count occurrences of each log level.

    Returns:
        {
            "counts"      : Counter({"INFO": N, "ERROR": N, ...}),
            "errors"      : [list of ERROR lines],
            "total_lines" : int
        }
    """
    counts: Counter = Counter()
    total: int = 0

    # List comprehension — collect all lines first so we can slice later
    # This is fine because we're doing analysis, not streaming production logs
    all_lines = [line for line in stream_log_lines(log_path)]
    total = len(all_lines)

    # Another comprehension — only ERROR lines
    error_lines = [line for line in all_lines if "ERROR" in line]

    # Loop through all lines, use regex to find and count levels
    for line in all_lines:
        match = LOG_PATTERN.search(line)
        if match:
            level = match.group(1)   # extract the captured group
            counts[level] += 1       # Counter handles missing keys gracefully

    logger.info(f"Analyzed {total} lines from {log_path}")

    return {
        "counts"      : counts,
        "errors"      : error_lines,
        "total_lines" : total,
    }


# ── Formatter ──────────────────────────────────────────────────────────────────

def format_analysis(result: dict) -> str:
    """Format the analysis result dict into a readable report string."""
    counts = result["counts"]

    lines = [
        "\n── Log Analysis ──────────────────────",
        f"  Total lines : {result['total_lines']}",
        f"  ERROR       : {counts.get('ERROR', 0)}",
        f"  WARNING     : {counts.get('WARNING', 0)}",
        f"  INFO        : {counts.get('INFO', 0)}",
        f"  DEBUG       : {counts.get('DEBUG', 0)}",
    ]

    # Only show recent errors section if there are any
    if result["errors"]:
        lines.append("\n  Recent Errors (last 5):")

        # List comprehension — take last 5 errors, indent each one
        recent = [f"    {e}" for e in result["errors"][-5:]]
        lines.extend(recent)

    return "\n".join(lines)