"""
utils/logger.py
---------------
Central logging setup for the entire CLI.
Call setup_logger() once at startup — all modules
that use logging.getLogger(__name__) inherit it.
Concepts: logging, handlers, formatters, pathlib
"""

import logging
import sys
from pathlib import Path


def setup_logger(
    log_path: str = "logs/app.log",
    level: str = "INFO"
) -> logging.Logger:
    """
    Configure the root logger to write to both file and terminal.

    Args:
        log_path : where to save the log file
        level    : minimum level to capture (DEBUG/INFO/WARNING/ERROR)

    Returns:
        The configured root logger.
    """

    # ── 1. Make sure the logs/ folder exists ──────────────
    # If log_path = "logs/app.log", this creates the "logs" folder
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    # ── 2. Convert level string → logging constant ────────
    # "INFO" → logging.INFO (which is just the integer 20)
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # ── 3. Define the log line format ─────────────────────
    log_format = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s"
    date_fmt   = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_fmt)

    # ── 4. Build the FILE handler ──────────────────────────
    # Appends to the log file, creates it if it doesn't exist
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)

    # ── 5. Build the TERMINAL handler ─────────────────────
    # Writes to stdout so you see logs in the terminal
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(numeric_level)

    # ── 6. Get the root logger and attach both handlers ───
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    return root_logger