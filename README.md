<div align="center">

```
██████╗ ███████╗██╗   ██╗ ██████╗ ██████╗ ███████╗      ██████╗██╗     ██╗
██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔══██╗██╔════╝     ██╔════╝██║     ██║
██║  ██║█████╗  ██║   ██║██║   ██║██████╔╝███████╗     ██║     ██║     ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝██║   ██║██╔═══╝ ╚════██║     ██║     ██║     ██║
██████╔╝███████╗ ╚████╔╝ ╚██████╔╝██║     ███████║     ╚██████╗███████╗██║
╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝ ╚═╝     ╚══════╝      ╚═════╝╚══════╝╚═╝
```

### 🛠️ A professional command-line tool that automates developer workflows
### Built from scratch in Python — system monitoring, log analysis, config management & more

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)

</div>

---

## 📌 What Is This?

**DevOps CLI** is a command-line automation tool that replaces repetitive terminal work with clean, structured commands. Instead of manually running scripts, checking system resources, or hunting through log files — this tool does it all in one place.

This is **Project 1** of my Python learning journey — built step by step to master Python fundamentals, standard library modules, and real-world CLI development patterns.

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/CaptainAni187/DEVOPS-CLI.git
cd DEVOPS-CLI

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run your first command
python3 cli/main.py status
```

---

## 🖥️ Commands

```
python3 cli/main.py <command> [options]
```

| Command | Options | What it does |
|---|---|---|
| `init` | — | Creates `logs/` `backups/` `temp/` `data/` folders |
| `status` | — | Project config + live CPU / RAM / Disk snapshot |
| `monitor` | `-n N` `--parallel` | Live system resource monitoring |
| `run` | `<cmd> [args]` | Run any shell command and capture output |
| `backup` | `[file]` | Backup a file with a timestamp in the name |
| `analyze-logs` | `[file]` | Parse log file — count ERROR / WARNING / INFO |
| `env` | — | Show `.env` variables (secrets auto-redacted) |

---

## 📺 Example Output

```
$ python3 cli/main.py status

── Project Status ────────────────────────
  Project  : myapp
  Log file : logs/app.log
  Backups  : backups
  Interval : 5s
  Level    : INFO

── System Monitor ────────────────────
  Time       : 2026-03-17 10:22:01
  CPU        : 35.0%
  RAM        : 61.4%
  Disk       : 72.1%
  Processes  : 387
```

```
$ python3 cli/main.py analyze-logs

── Log Analysis ──────────────────────
  Total lines : 143
  ERROR       : 3
  WARNING     : 12
  INFO        : 128
  DEBUG       : 0

  Recent Errors (last 5):
    2026-03-17 10:00:05  ERROR  Failed to connect
    2026-03-17 10:00:08  ERROR  Command timed out
```

```
$ python3 cli/main.py env

── Environment Variables ──────────────
  DATABASE_URL         = ****
  API_KEY              = ****
  ENVIRONMENT          = development
  DEBUG                = true
```

---

## 🏗️ Project Structure

```
devops-cli/
│
├── cli/
│   └── main.py               ← Entry point — argparse, dispatch table
│
├── core/
│   ├── config_loader.py      ← Loads config.yaml → Config dataclass
│   ├── command_runner.py     ← Runs shell commands via subprocess
│   ├── log_analyzer.py       ← Parses logs with regex + Counter
│   └── system_monitor.py     ← CPU / RAM / Disk via psutil + threading
│
├── utils/
│   ├── logger.py             ← Central logging to file + terminal
│   ├── helpers.py            ← File backup, dirs, temp workspaces
│   └── env_manager.py        ← .env loading + secret redaction
│
├── models/
│   └── config_model.py       ← Config dataclass + LogLevel enum
│
├── data/
│   └── config.yaml           ← Project configuration
│
├── tests/
│   ├── conftest.py           ← Shared pytest fixtures
│   └── test_devops.py        ← 38 unit tests
│
├── .env.example              ← Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 What I Learned Building This

This project was built to deliberately practice every core Python concept. Here's exactly what each module taught me:

---

### 📦 Data Structures & OOP — `models/config_model.py`

```python
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"

@dataclass
class Config:
    project_name: str
    log_level: LogLevel = LogLevel.INFO
```

| Concept | What I learned |
|---|---|
| `@dataclass` | Auto-generates `__init__`, `__repr__` — no boilerplate |
| `Enum` | Named constants that prevent typos — `LogLevel.ERROR` not `"ERORR"` |
| Type hints | `str`, `int`, `Optional[str]` — documents what functions expect |
| `__post_init__` | Runs after `__init__` — converts raw strings to enum values |

---

### 📂 File Handling & Caching — `core/config_loader.py`

```python
from functools import lru_cache
import yaml

@lru_cache(maxsize=1)
def load_config(path: str = CONFIG_PATH) -> Config:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    ...
```

| Concept | What I learned |
|---|---|
| `PyYAML` | Parse `.yaml` files into Python dicts with `yaml.safe_load()` |
| `pathlib.Path` | OS-safe paths using `/` operator — works on Mac, Linux, Windows |
| `@lru_cache` | Cache expensive results — file is only read once per session |
| `with open()` | Context manager — auto-closes files even if an error occurs |
| Set subtraction | `required_keys - raw.keys()` to find missing config fields |

---

### ⚙️ Subprocess & Exception Handling — `core/command_runner.py`

```python
import subprocess, traceback

try:
    result = subprocess.run(command, capture_output=True, text=True)
except subprocess.TimeoutExpired:
    ...
except FileNotFoundError:
    ...
finally:
    logger.debug("Command attempt finished")
```

| Concept | What I learned |
|---|---|
| `subprocess.run()` | Run real shell commands — `pytest`, `git`, `docker` — from Python |
| `capture_output=True` | Capture stdout and stderr as strings instead of printing to terminal |
| `returncode` | `0` = success, anything else = failure — universal convention |
| `try/except/finally` | Handle timeout, missing command, and unexpected errors cleanly |
| `traceback.format_exc()` | Capture full stack trace for debugging without crashing the user |
| `Optional[str]` | Type hint for values that can be a string or `None` |

---

### 🔍 Regex, Generators & Comprehensions — `core/log_analyzer.py`

```python
import re
from collections import Counter

LOG_PATTERN = re.compile(r"\b(ERROR|WARNING|INFO|DEBUG)\b")

def stream_log_lines(path):       # Generator — one line at a time
    with open(path) as f:
        for line in f:
            yield line

errors = [line for line in lines if "ERROR" in line]   # List comprehension
```

| Concept | What I learned |
|---|---|
| `re.compile()` | Compile regex once, reuse in loops — faster than inline patterns |
| `\b(ERROR\|WARNING)\b` | Word boundaries prevent `INFORMATIONAL` matching `INFO` |
| `match.group(1)` | Extract the captured group from a regex match |
| `yield` generator | Produces one item at a time — memory-efficient for huge files |
| `collections.Counter` | Dictionary built for counting — missing keys return `0` not `KeyError` |
| List comprehension | `[x for x in items if condition]` — filter and transform in one line |
| Dict comprehension | `{k: v for k, v in pairs}` — build dicts with filtering inline |

---

### 🖥️ System Monitoring & Concurrency — `core/system_monitor.py`

```python
import psutil, threading

def monitor_loop():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

t1 = threading.Thread(target=monitor_loop, daemon=True)
t2 = threading.Thread(target=analyze_logs)
t1.start(); t2.start()
t1.join();  t2.join()
```

| Concept | What I learned |
|---|---|
| `psutil` | Read real CPU, RAM, Disk, process count from the OS |
| `datetime.strftime()` | Format timestamps — `%Y-%m-%d %H:%M:%S` → `2026-03-17 10:22:01` |
| `threading.Thread` | Run two functions simultaneously in parallel |
| `t.start()` / `t.join()` | Launch a thread / wait for it to finish |
| `daemon=True` | Thread dies when main program exits — prevents hanging |
| Shared dict | Pass a mutable dict into a thread to receive results back |

---

### 📝 Logging System — `utils/logger.py`

```python
import logging

formatter   = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")
file_handler   = logging.FileHandler("logs/app.log")
stream_handler = logging.StreamHandler(sys.stdout)
```

| Concept | What I learned |
|---|---|
| Log levels | `DEBUG → INFO → WARNING → ERROR` — filter noise by level |
| `FileHandler` | Write log lines to a persistent file on disk |
| `StreamHandler` | Write log lines to the terminal simultaneously |
| `Formatter` | Control the exact shape of each log line |
| `getLogger(__name__)` | Each module gets its own named logger — inherit root config |

---

### 🗂️ File System Automation — `utils/helpers.py`

```python
import shutil, tempfile
from pathlib import Path

shutil.copy2(src, dest)          # Copy with metadata preserved
tmp = tempfile.mkdtemp()         # Safe random temp directory
Path(dir).rglob("*")             # Walk entire directory tree
```

| Concept | What I learned |
|---|---|
| `Path.mkdir(parents=True)` | Create full folder chain in one call |
| `shutil.copy2()` | Copy files preserving timestamps and permissions |
| `tempfile.mkdtemp()` | Create temp folders with random names — never clash |
| `Path.rglob("*")` | Recursively walk every file in a directory tree |
| `path.stem` / `path.suffix` | Split `config.yaml` → `config` + `.yaml` |

---

### 🔐 Environment Variables — `utils/env_manager.py`

```python
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv(".env", override=False)
value = os.environ.get("API_KEY", "default")
```

| Concept | What I learned |
|---|---|
| `load_dotenv()` | Push `.env` file contents into `os.environ` |
| `override=False` | Real env variables take priority over `.env` defaults |
| `dotenv_values()` | Read `.env` as a dict without touching `os.environ` |
| Secret redaction | Dict comprehension replaces sensitive values with `****` |

---

### 🖱️ CLI Interface — `cli/main.py`

```python
import argparse, sys

sub = parser.add_subparsers(dest="command")
sub.add_parser("monitor").add_argument("-n", "--count", type=int)

COMMANDS = {
    "monitor" : cmd_monitor,
    "backup"  : cmd_backup,
}
handler = COMMANDS.get(args.command)
handler(args)
```

| Concept | What I learned |
|---|---|
| `argparse` subparsers | One tool, multiple sub-commands like `git commit`, `git push` |
| `action="store_true"` | Boolean flags — present = True, absent = False |
| `nargs=REMAINDER` | Capture everything after a command as-is |
| Dispatch table | Dict of `{command: function}` replaces long `if/elif` chains |
| `sys.path.insert()` | Tell Python where to find modules at runtime |
| `KeyboardInterrupt` | Catch `Ctrl+C` for a clean exit instead of an ugly traceback |
| `sys.exit(0/1)` | `0` = success, `1` = error — other programs read this |

---

### 🧪 Testing — `tests/test_devops.py`

```python
import pytest
from unittest.mock import patch, MagicMock

def test_snapshot_uses_mocked_psutil():
    with patch("core.system_monitor.psutil") as mock:
        mock.cpu_percent.return_value = 42.0
        snap = get_snapshot()
        assert snap["cpu"] == 42.0

def test_backup_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup_file("/nonexistent/file.yaml")
```

| Concept | What I learned |
|---|---|
| `pytest` | Test runner — finds and runs any function starting with `test_` |
| `tmp_path` fixture | Built-in temporary folder — cleaned up after each test |
| `@pytest.fixture` | Reusable setup shared across multiple tests |
| `pytest.raises()` | Assert that a specific exception is raised |
| `patch()` | Replace real functions with fakes during a test |
| `MagicMock` | Fake object that accepts any method call without crashing |
| `assert_called_once_with()` | Verify a mock was called with exact arguments |

---

## 🧪 Running Tests

```bash
# Run all 38 tests
pytest tests/ -v

# Run one class of tests
pytest tests/ -v -k TestLogAnalyzer

# Run with coverage report
pip install pytest-cov
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 📚 Dependencies

```
psutil          — System resource monitoring (CPU, RAM, Disk)
python-dotenv   — Load .env files into environment variables  
PyYAML          — Parse YAML configuration files
pytest          — Testing framework
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🗺️ What's Next

This project can be extended into more advanced territory:

- [ ] `devops schedule` — run commands on a cron-style timer using `sched`
- [ ] `devops clean` — delete temp files and old backups
- [ ] `--output json` flag — machine-readable output for scripting
- [ ] SSH automation using `paramiko` — run commands on remote servers
- [ ] Docker control commands — `docker build`, `docker ps`, `docker logs`

---

## 👨‍💻 About

Built by **[@CaptainAni187](https://github.com/CaptainAni187)** as Project 1 of a structured Python learning path — progressing from fundamentals through intermediate patterns to production-ready code.

---

<div align="center">

**⭐ Star this repo if it helped you learn something**

</div>