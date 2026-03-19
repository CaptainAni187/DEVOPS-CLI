"""
utils/env_manager.py
---------------------
Load .env files and expose environment variables safely.
Concepts: os.environ, python-dotenv, dict comprehensions,
          redacting sensitive values
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

logger = logging.getLogger(__name__)

# Any key containing these words will have its value redacted
# when displayed — never show secrets in terminal output
SENSITIVE_KEYWORDS = {"KEY", "SECRET", "PASSWORD", "TOKEN", "URL", "PWD"}


def _is_sensitive(key: str) -> bool:
    """Return True if key name suggests it holds a sensitive value."""
    return any(word in key.upper() for word in SENSITIVE_KEYWORDS)


# ── Load ───────────────────────────────────────────────────────────────────────

def load_env(env_file: str = ".env") -> bool:
    """
    Load variables from .env into os.environ.
    After this call, os.environ.get("API_KEY") works normally.

    override=False means existing os.environ values are NOT
    overwritten — real environment variables take priority.

    Returns True if file was found and loaded, False if not found.
    """
    path = Path(env_file)

    if not path.exists():
        logger.warning(f".env file not found: {path}")
        return False

    load_dotenv(dotenv_path=path, override=False)
    logger.info(f"Loaded env file: {path}")
    return True


# ── Read Single Variable ───────────────────────────────────────────────────────

def get_env(key: str, default: str = "") -> str:
    """
    Read a single environment variable.
    Returns default if not set — never raises KeyError.
    """
    value = os.environ.get(key, default)
    if not value:
        logger.warning(f"Environment variable not set: {key}")
    return value


# ── List All Variables ─────────────────────────────────────────────────────────

def list_env(env_file: str = ".env") -> dict[str, str]:
    """
    Read all key-value pairs from .env file.
    Does NOT modify os.environ — purely reads the file.
    Sensitive values are replaced with **** for safe display.

    Returns a dict with secrets redacted.
    """
    # dotenv_values reads the file without touching os.environ
    raw_values = dotenv_values(env_file)

    # Dict comprehension — redact sensitive values
    # For each k,v pair: if key is sensitive show ****, else show real value
    return {
        k: ("****" if _is_sensitive(k) else v)
        for k, v in raw_values.items()
    }


# ── Format for Display ─────────────────────────────────────────────────────────

def format_env(env_file: str = ".env") -> str:
    """
    Return a formatted string of env variables safe to print.
    Sensitive values are already redacted by list_env().
    """
    pairs = list_env(env_file)

    if not pairs:
        return "  No environment variables found in .env"

    lines = ["\n── Environment Variables ──────────────"]

    # F-string with format spec — k left-aligned in 20-char column
    lines += [f"  {k:<20} = {v}" for k, v in pairs.items()]

    return "\n".join(lines)