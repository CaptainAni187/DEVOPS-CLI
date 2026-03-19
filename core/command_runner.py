"""
core/command_runner.py
----------------------
Runs external shell commands via subprocess.
Captures output, handles errors, logs everything.
Concepts: subprocess, exception handling, traceback, type hints
"""

import subprocess
import logging
import traceback
from typing import Optional

# Named logger for this module — inherits root config from setup_logger()
logger = logging.getLogger(__name__)


def run_command(
    command: list[str],
    cwd: Optional[str] = None,
    timeout: int = 120,
) -> dict:
    """
    Run an external command and return a result dictionary.

    Args:
        command : list of strings e.g. ["pytest", "--verbose"]
        cwd     : working directory to run command in (None = current dir)
        timeout : seconds before killing the command (default 120)

    Returns:
        {
            "success"    : bool,
            "stdout"     : str,
            "stderr"     : str,
            "returncode" : int
        }
    """

    # Join list to string just for readable log messages
    cmd_str = " ".join(command)
    logger.info(f"Running: {cmd_str}")

    try:
        # ── Run the command ────────────────────────────────────
        result = subprocess.run(
            command,
            capture_output=True,   # capture stdout + stderr
            text=True,             # return strings not bytes
            cwd=cwd,               # working directory
            timeout=timeout,       # kill if it takes too long
        )

        # ── Log based on success or failure ───────────────────
        if result.returncode == 0:
            logger.info(f"Success: {cmd_str}")
        else:
            logger.warning(f"Failed (code {result.returncode}): {cmd_str}")
            if result.stderr:
                logger.error(f"STDERR: {result.stderr.strip()}")

        return {
            "success"    : result.returncode == 0,
            "stdout"     : result.stdout.strip(),
            "stderr"     : result.stderr.strip(),
            "returncode" : result.returncode,
        }

    except subprocess.TimeoutExpired:
        # ── Command ran too long ───────────────────────────────
        logger.error(f"Timed out after {timeout}s: {cmd_str}")
        return {
            "success"    : False,
            "stdout"     : "",
            "stderr"     : f"Command timed out after {timeout}s",
            "returncode" : -1,
        }

    except FileNotFoundError:
        # ── Command doesn't exist on this machine ──────────────
        logger.error(f"Command not found: {command[0]}")
        return {
            "success"    : False,
            "stdout"     : "",
            "stderr"     : f"Command not found: {command[0]}",
            "returncode" : -1,
        }

    except Exception as e:
        # ── Anything else unexpected ───────────────────────────
        # Log full stack trace to file for debugging
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        return {
            "success"    : False,
            "stdout"     : "",
            "stderr"     : str(e),
            "returncode" : -1,
        }

    finally:
        # ── Always runs — success or failure ──────────────────
        logger.debug(f"Command attempt finished: {cmd_str}")