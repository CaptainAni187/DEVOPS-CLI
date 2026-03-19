"""
tests/conftest.py
-----------------
Shared fixtures available to all test files automatically.
pytest finds this file and makes everything here available
without any imports in the test files themselves.
"""

import sys
import pytest
from pathlib import Path

# Make sure project root is on the path for all tests
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_log_file(tmp_path):
    """
    Creates a realistic log file in a temp folder.
    tmp_path is provided by pytest — fresh folder per test,
    deleted automatically when the test finishes.
    """
    log = tmp_path / "app.log"
    log.write_text(
        "2026-03-17 10:00:01  INFO     Application started\n"
        "2026-03-17 10:00:02  INFO     Config loaded\n"
        "2026-03-17 10:00:03  DEBUG    Raw value: 42\n"
        "2026-03-17 10:00:04  WARNING  Disk usage above 70%\n"
        "2026-03-17 10:00:05  ERROR    Failed to connect\n"
        "2026-03-17 10:00:06  INFO     Retrying...\n"
        "2026-03-17 10:00:07  WARNING  Retry 1 of 3\n"
        "2026-03-17 10:00:08  ERROR    Command timed out\n"
        "2026-03-17 10:00:09  INFO     Shutdown complete\n"
    )
    return str(log)


@pytest.fixture
def sample_config_file(tmp_path):
    """Creates a valid config.yaml in a temp folder."""
    config = tmp_path / "config.yaml"
    config.write_text(
        "project_name: testapp\n"
        "log_path: logs/app.log\n"
        "backup_dir: backups\n"
        "monitor_interval: 3\n"
        "log_level: INFO\n"
    )
    return str(config)


@pytest.fixture
def empty_log_file(tmp_path):
    """Creates an empty log file."""
    log = tmp_path / "empty.log"
    log.write_text("")
    return str(log)