"""
core/config_loader.py
---------------------
Loads config.yaml and returns a validated Config dataclass.
Concepts: PyYAML, pathlib, lru_cache, file handling, validation
"""

import yaml
from functools import lru_cache
from pathlib import Path

from models.config_model import Config, LogLevel


# Build the path to config.yaml relative to this file's location
# __file__ = core/config_loader.py
# .parent   = core/
# .parent   = devops-cli/       ← project root
# / "data" / "config.yaml"      = devops-cli/data/config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.yaml"


@lru_cache(maxsize=1)
def load_config(path: str = str(CONFIG_PATH)) -> Config:
    """
    Read config.yaml → validate → return Config dataclass.
    lru_cache means this only runs once — subsequent calls
    return the cached result instantly.
    """

    config_file = Path(path)

    # ── 1. Check the file exists ──────────────────────────
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # ── 2. Read and parse YAML ────────────────────────────
    with open(config_file, "r") as f:
        raw = yaml.safe_load(f)

    # ── 3. Handle empty file ──────────────────────────────
    if raw is None:
        raise ValueError("Config file is empty.")

    # ── 4. Validate required keys exist ───────────────────
    required_keys = {"project_name", "log_path", "backup_dir", "monitor_interval"}
    missing = required_keys - raw.keys()  # set subtraction
    if missing:
        raise KeyError(f"Config is missing required keys: {missing}")

    # ── 5. Build and return the Config dataclass ──────────
    return Config(
        project_name=raw["project_name"],
        log_path=raw["log_path"],
        backup_dir=raw["backup_dir"],
        monitor_interval=int(raw["monitor_interval"]),
        log_level=LogLevel(raw.get("log_level", "INFO").upper()),
    )