"""
utils/helpers.py
-----------------
File system utilities — directory creation, backups, temp workspaces.
Concepts: pathlib, shutil, tempfile, os, datetime, comprehensions
"""

import os
import shutil
import tempfile
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Project Initialisation ─────────────────────────────────────────────────────

def init_project_dirs(base: str = ".") -> list[str]:
    """
    Create standard project directories under base path.
    Safe to call multiple times — exist_ok=True means no errors
    if directories already exist.

    Returns list of directory paths that were created/confirmed.
    """
    # The folders every project needs
    dir_names = ["logs", "backups", "temp", "data"]
    created = []

    for name in dir_names:
        path = Path(base) / name

        # parents=True  — create full chain if needed
        # exist_ok=True — don't raise error if already exists
        path.mkdir(parents=True, exist_ok=True)
        created.append(str(path))
        logger.info(f"Directory ready: {path}")

    return created


# ── File Backup ────────────────────────────────────────────────────────────────

def backup_file(source: str, backup_dir: str = "backups") -> str:
    """
    Copy a file to backup_dir with a timestamp in the filename.
    Original file is never modified.

    Example:
        config.yaml → backups/config_20260317_102201.yaml

    Returns the full path of the backup file created.
    """
    src = Path(source)

    # Validate source exists before doing anything
    if not src.exists():
        raise FileNotFoundError(f"Cannot backup — file not found: {src}")

    # Ensure backup destination folder exists
    dest_dir = Path(backup_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Build timestamped filename
    # src.stem   = "config"   (filename without extension)
    # src.suffix = ".yaml"    (just the extension)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"{src.stem}_{timestamp}{src.suffix}"
    dest = dest_dir / dest_name

    # copy2 preserves metadata (timestamps, permissions)
    shutil.copy2(src, dest)
    logger.info(f"Backup created: {src} → {dest}")

    return str(dest)


# ── List Backups ───────────────────────────────────────────────────────────────

def list_backups(backup_dir: str = "backups") -> list[str]:
    """
    Return sorted list of all backup files.
    List comprehension — only include files, not subdirectories.
    """
    path = Path(backup_dir)

    if not path.exists():
        logger.warning(f"Backup directory not found: {path}")
        return []

    # List comprehension — f for each item in directory if it's a file
    return sorted([str(f) for f in path.iterdir() if f.is_file()])


# ── Temporary Workspace ────────────────────────────────────────────────────────

def create_temp_workspace() -> str:
    """
    Create a temporary directory for scratch work.
    Returns the path as a string.

    Caller should delete it when done using:
        shutil.rmtree(tmp_path)
    """
    tmp = tempfile.mkdtemp(prefix="devops_")
    logger.debug(f"Temp workspace created: {tmp}")
    return tmp


# ── Directory Size ─────────────────────────────────────────────────────────────

def get_dir_size(path: str = ".") -> str:
    """
    Calculate total size of all files in a directory tree.
    Uses rglob("*") to walk recursively.
    Returns human-readable string like "4.2 MB".
    """
    total_bytes = sum(
        # Generator expression — like list comprehension but no list built
        f.stat().st_size
        for f in Path(path).rglob("*")
        if f.is_file()
    )

    # Convert bytes → readable units
    for unit in ["B", "KB", "MB", "GB"]:
        if total_bytes < 1024:
            return f"{total_bytes:.1f} {unit}"
        total_bytes /= 1024

    return f"{total_bytes:.1f} TB"