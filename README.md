<div align="center">

# DevOps Automation CLI

### A command-line tool that automates developer workflows — system monitoring, log analysis, config management, and subprocess automation

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

</div>

---

## Overview

**DevOps CLI** is a command-line automation tool that replaces repetitive terminal work with clean, structured commands. Instead of manually running scripts, checking system resources, or hunting through log files — this tool handles it all through a single unified interface.

Built from scratch in Python using only the standard library and a small set of well-chosen third-party packages. Every module is intentionally structured to demonstrate clean separation of concerns, robust error handling, and professional code organisation.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/CaptainAni187/DEVOPS-CLI.git
cd DEVOPS-CLI

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run your first command
python3 cli/main.py status
```

---

## Commands

```
python3 cli/main.py <command> [options]
```

| Command | Options | Description |
|---|---|---|
| `init` | — | Creates `logs/` `backups/` `temp/` `data/` directories |
| `status` | — | Displays project config and a live system snapshot |
| `monitor` | `-n N` `--parallel` | Live CPU / RAM / Disk monitoring |
| `run` | `<cmd> [args]` | Execute any shell command and capture its output |
| `backup` | `[file]` | Backup a file with a timestamp appended to the filename |
| `analyze-logs` | `[file]` | Parse a log file and report ERROR / WARNING / INFO counts |
| `env` | — | Display `.env` variables with sensitive values redacted |

---

## Example Output

```
$ python3 cli/main.py status

-- Project Status ----------------------------------------
  Project  : myapp
  Log file : logs/app.log
  Backups  : backups
  Interval : 5s
  Level    : INFO

-- System Monitor ----------------------------------------
  Time       : 2026-03-17 10:22:01
  CPU        : 35.0%
  RAM        : 61.4%
  Disk       : 72.1%
  Processes  : 387
```

```
$ python3 cli/main.py analyze-logs

-- Log Analysis ------------------------------------------
  Total lines : 143
  ERROR       : 3
  WARNING     : 12
  INFO        : 128
  DEBUG       : 0

  Recent Errors (last 5):
    2026-03-17 10:00:05  ERROR  Failed to connect to database
    2026-03-17 10:00:08  ERROR  Command timed out after 30s
```

```
$ python3 cli/main.py env

-- Environment Variables ---------------------------------
  DATABASE_URL         = ****
  API_KEY              = ****
  ENVIRONMENT          = development
  DEBUG                = true
```

---

## Project Structure

```
devops-cli/
│
├── cli/
│   └── main.py               Entry point — argparse subcommands, dispatch table
│
├── core/
│   ├── config_loader.py      Loads config.yaml into a validated Config dataclass
│   ├── command_runner.py     Runs shell commands via subprocess, captures output
│   ├── log_analyzer.py       Parses log files using regex and Counter
│   └── system_monitor.py     CPU / RAM / Disk stats via psutil with threading
│
├── utils/
│   ├── logger.py             Central logging to both file and terminal
│   ├── helpers.py            File backup, directory management, temp workspaces
│   └── env_manager.py        .env loading and sensitive value redaction
│
├── models/
│   └── config_model.py       Config dataclass and LogLevel enum
│
├── data/
│   └── config.yaml           Project configuration
│
├── tests/
│   ├── conftest.py           Shared pytest fixtures
│   └── test_devops.py        38 unit tests covering all modules
│
├── .env.example              Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `psutil` | System resource monitoring — CPU, RAM, Disk, process count |
| `python-dotenv` | Load `.env` files into environment variables |
| `PyYAML` | Parse YAML configuration files |
| `pytest` | Testing framework |

```bash
pip install -r requirements.txt
```

---

## Running Tests

```bash
# Run all 38 tests with verbose output
pytest tests/ -v

# Run a specific test class
pytest tests/ -v -k TestLogAnalyzer

# Run with coverage report
pip install pytest-cov
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## Concepts Covered

This project was built to deliberately practice and demonstrate core Python concepts across every module.

---

### Data Structures and OOP — `models/config_model.py`

```python
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    INFO    = "INFO"
    ERROR   = "ERROR"
    WARNING = "WARNING"
    DEBUG   = "DEBUG"

@dataclass
class Config:
    project_name: str
    log_path:     str
    backup_dir:   str
    monitor_interval: int
    log_level: LogLevel = LogLevel.INFO

    def __post_init__(self):
        if isinstance(self.log_level, str):
            self.log_level = LogLevel(self.log_level.upper())
```

| Concept | Notes |
|---|---|
| `@dataclass` | Auto-generates `__init__` and `__repr__` — eliminates boilerplate |
| `Enum` | Named constants that prevent typos — `LogLevel.ERROR` not `"ERORR"` |
| Type hints | `str`, `int`, `Optional[str]` — documents function contracts clearly |
| `__post_init__` | Runs after `__init__` — converts raw strings to enum values automatically |

---

### File Handling and Caching — `core/config_loader.py`

```python
from functools import lru_cache
import yaml

@lru_cache(maxsize=1)
def load_config(path: str = CONFIG_PATH) -> Config:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    required = {"project_name", "log_path", "backup_dir", "monitor_interval"}
    missing = required - raw.keys()
    if missing:
        raise KeyError(f"Missing config keys: {missing}")
    return Config(...)
```

| Concept | Notes |
|---|---|
| `PyYAML` | Parses `.yaml` files into Python dicts with `yaml.safe_load()` |
| `pathlib.Path` | OS-safe path joining using `/` operator — works across all platforms |
| `@lru_cache` | Caches the result — config file is read from disk only once per session |
| `with open()` | Context manager — file is closed automatically even if an error occurs |
| Set subtraction | `required - raw.keys()` finds missing configuration fields in one operation |

---

### Subprocess and Exception Handling — `core/command_runner.py`

```python
import subprocess, traceback

try:
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=timeout
    )
except subprocess.TimeoutExpired:
    return {"success": False, "stderr": "Command timed out"}
except FileNotFoundError:
    return {"success": False, "stderr": f"Command not found: {command[0]}"}
finally:
    logger.debug(f"Command attempt finished: {cmd_str}")
```

| Concept | Notes |
|---|---|
| `subprocess.run()` | Execute real shell commands — `pytest`, `git`, `docker` — from Python |
| `capture_output=True` | Captures stdout and stderr as strings rather than printing to terminal |
| `returncode` | `0` = success, non-zero = failure — a universal convention across all OS |
| `try/except/finally` | Handles timeout, missing command, and unexpected errors independently |
| `traceback.format_exc()` | Captures full stack trace to log file without exposing it to the user |

---

### Regex, Generators and Comprehensions — `core/log_analyzer.py`

```python
import re
from collections import Counter

LOG_PATTERN = re.compile(r"\b(ERROR|WARNING|INFO|DEBUG)\b")

def stream_log_lines(path) -> Generator[str, None, None]:
    with open(path) as f:
        for line in f:
            yield line.rstrip()

error_lines = [line for line in all_lines if "ERROR" in line]
safe_env    = {k: "****" if _is_sensitive(k) else v for k, v in pairs.items()}
```

| Concept | Notes |
|---|---|
| `re.compile()` | Compiles the pattern once and reuses it — more efficient inside loops |
| Word boundaries `\b` | Prevents `INFORMATIONAL` from matching `INFO` |
| `match.group(1)` | Extracts the captured group from a regex match |
| `yield` generator | Produces one line at a time — constant memory use regardless of file size |
| `collections.Counter` | Dictionary built for counting — missing keys return `0` not `KeyError` |
| List comprehension | `[x for x in items if condition]` — filter and transform in one expression |
| Dict comprehension | `{k: v for k, v in pairs if condition}` — build transformed dicts inline |

---

### System Monitoring and Concurrency — `core/system_monitor.py`

```python
import psutil, threading

snap = {
    "cpu"       : psutil.cpu_percent(interval=1),
    "ram"       : psutil.virtual_memory().percent,
    "disk"      : psutil.disk_usage("/").percent,
    "processes" : len(psutil.pids()),
}

t1 = threading.Thread(target=monitor_loop, daemon=True)
t2 = threading.Thread(target=analyze_logs)
t1.start(); t2.start()
t1.join();  t2.join()
```

| Concept | Notes |
|---|---|
| `psutil` | Reads real CPU, RAM, Disk, and process counts from the operating system |
| `datetime.strftime()` | Formats timestamps — `%Y-%m-%d %H:%M:%S` produces `2026-03-17 10:22:01` |
| `threading.Thread` | Runs two functions simultaneously in parallel |
| `daemon=True` | Thread is killed automatically when the main process exits |
| `t.join()` | Blocks until the thread finishes — prevents premature program exit |
| Shared mutable dict | Threads write results into a shared dict the main thread reads after |

---

### Logging System — `utils/logger.py`

```python
import logging, sys

formatter      = logging.Formatter("%(asctime)s  %(levelname)-8s  %(name)s -- %(message)s")
file_handler   = logging.FileHandler("logs/app.log")
stream_handler = logging.StreamHandler(sys.stdout)

root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)
```

| Concept | Notes |
|---|---|
| Log levels | `DEBUG < INFO < WARNING < ERROR` — controls what gets recorded |
| `FileHandler` | Writes log lines to a persistent file on disk |
| `StreamHandler` | Writes log lines to the terminal at the same time |
| `Formatter` | Controls the exact shape and content of each log line |
| `getLogger(__name__)` | Named logger per module — shows which file produced each log line |

---

### File System Automation — `utils/helpers.py`

```python
import shutil, tempfile
from pathlib import Path

shutil.copy2(src, dest)
tmp   = tempfile.mkdtemp(prefix="devops_")
total = sum(f.stat().st_size
            for f in Path(path).rglob("*")
            if f.is_file())
```

| Concept | Notes |
|---|---|
| `Path.mkdir(parents=True, exist_ok=True)` | Creates full folder chain — no error if it already exists |
| `shutil.copy2()` | Copies a file and preserves timestamps and permissions |
| `tempfile.mkdtemp()` | Creates a temporary directory with a random non-clashing name |
| `Path.rglob("*")` | Recursively walks every file in a directory tree |
| `path.stem` / `path.suffix` | Splits `config.yaml` into `config` and `.yaml` |
| Generator expression | Like a list comprehension but does not allocate the full list in memory |

---

### Environment Variables — `utils/env_manager.py`

```python
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv(".env", override=False)
value = os.environ.get("API_KEY", "default-value")

safe = {
    k: ("****" if _is_sensitive(k) else v)
    for k, v in dotenv_values(".env").items()
}
```

| Concept | Notes |
|---|---|
| `load_dotenv()` | Pushes `.env` file contents into `os.environ` at startup |
| `override=False` | Existing environment variables take priority over `.env` defaults |
| `dotenv_values()` | Reads `.env` as a plain dict without modifying the environment |
| Secret redaction | Dict comprehension replaces sensitive values with `****` before display |

---

### CLI Interface — `cli/main.py`

```python
import argparse, sys

sub       = parser.add_subparsers(dest="command")
p_monitor = sub.add_parser("monitor")
p_monitor.add_argument("-n", "--count", type=int)
p_monitor.add_argument("--parallel", action="store_true")

COMMANDS = {
    "monitor"      : cmd_monitor,
    "backup"       : cmd_backup,
    "analyze-logs" : cmd_analyze_logs,
}
handler = COMMANDS.get(args.command)
handler(args)
```

| Concept | Notes |
|---|---|
| `argparse` subparsers | One tool, multiple sub-commands — same pattern as `git commit`, `git push` |
| `action="store_true"` | Boolean flag — present means `True`, absent means `False` |
| `nargs=REMAINDER` | Captures everything after a command including its own flags |
| Dispatch table | `{name: function}` dict replaces long `if/elif` chains — trivially extensible |
| `sys.path.insert()` | Adds the project root to Python's module search path at runtime |
| `KeyboardInterrupt` | Catches `Ctrl+C` for a clean exit rather than an ugly traceback |
| `sys.exit(0/1)` | `0` = success, `1` = error — readable by calling scripts and CI systems |

---

### Testing — `tests/test_devops.py`

```python
import pytest
from unittest.mock import patch, MagicMock

def test_snapshot_with_mocked_psutil():
    with patch("core.system_monitor.psutil") as mock_psutil:
        mock_psutil.cpu_percent.return_value = 42.0
        snap = get_snapshot()
        assert snap["cpu"] == 42.0

def test_backup_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup_file("/nonexistent/file.yaml", str(tmp_path))
```

| Concept | Notes |
|---|---|
| `pytest` | Test runner — discovers and runs any function prefixed with `test_` |
| `tmp_path` fixture | Built-in temporary directory — isolated per test, deleted automatically |
| `@pytest.fixture` | Reusable setup function injected into tests as a parameter |
| `pytest.raises()` | Asserts that a specific exception type is raised |
| `patch()` | Replaces a real function with a controllable fake for one test |
| `MagicMock` | Accepts any attribute or method call — returns configured values |
| `assert_called_once_with()` | Verifies a mock was called with the exact expected arguments |

---

## Possible Extensions

| Feature | Approach |
|---|---|
| `devops schedule` | Cron-style task runner using Python's `sched` module |
| `devops clean` | Remove temp files and prune old backups automatically |
| `--output json` | Machine-readable output flag for scripting and CI pipelines |
| Remote automation | SSH command execution using `paramiko` |
| Docker integration | `docker build`, `docker ps`, `docker logs` via subprocess |

---

<div align="center">

Built by [@CaptainAni187](https://github.com/CaptainAni187)

</div>