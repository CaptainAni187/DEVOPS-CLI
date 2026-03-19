"""
cli/main.py
-----------
Entry point for the DevOps Automation CLI.
Wires all modules together under one argparse interface.
Concepts: argparse subparsers, sys.path, dispatch table,
          exception handling, KeyboardInterrupt, sys.exit
"""

import sys
import argparse
import logging
import traceback
import threading
from pathlib import Path

# ── Fix import path ────────────────────────────────────────────────────────────
# __file__ is cli/main.py — we need to go up one level to project root
# so Python can find core/, utils/, models/
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── Import all modules built in previous steps ─────────────────────────────────
from utils.logger      import setup_logger
from utils.helpers     import init_project_dirs, backup_file, list_backups
from utils.env_manager import load_env, format_env
from core.config_loader  import load_config
from core.command_runner import run_command
from core.log_analyzer   import analyze_logs, format_analysis
from core.system_monitor import get_snapshot, format_snapshot, monitor_loop, run_parallel


# ══════════════════════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# Each function handles one subcommand.
# They all receive `args` from argparse and return nothing.
# ══════════════════════════════════════════════════════════════════════════════

def cmd_init(args) -> None:
    """devops init — create standard project folders."""
    print("\n── Initialising project ──────────────────")
    created = init_project_dirs()
    for d in created:
        print(f"  ✓  {d}")
    print("\nProject ready.\n")


def cmd_run(args) -> None:
    """devops run <command> [args...] — run any external command."""
    if not args.cmd:
        print("Usage: devops run <command> [args...]")
        print("Examples:")
        print("  devops run pytest")
        print("  devops run git status")
        print("  devops run python3 --version")
        sys.exit(1)

    result = run_command(args.cmd)

    print(f"\n── Command: {' '.join(args.cmd)} {'─'*20}")
    print(f"  Status : {'✓ Success' if result['success'] else '✗ Failed'}")
    print(f"  Code   : {result['returncode']}")

    if result["stdout"]:
        print(f"\n  Output:\n")
        # Indent each line of output for clean display
        for line in result["stdout"].splitlines():
            print(f"    {line}")

    if result["stderr"]:
        print(f"\n  Errors:\n")
        for line in result["stderr"].splitlines():
            print(f"    {line}")

    print()

    # Mirror the command's exit code so scripts can detect failure
    if not result["success"]:
        sys.exit(result["returncode"])


def cmd_backup(args) -> None:
    """devops backup [file] — backup a file with a timestamp."""
    cfg = load_config()
    target = args.file or "data/config.yaml"

    print(f"\n── Backup ────────────────────────────────")

    try:
        dest = backup_file(target, cfg.backup_dir)
        print(f"  ✓  {target}")
        print(f"  →  {dest}")
    except FileNotFoundError as e:
        print(f"  ✗  {e}")
        sys.exit(1)

    # Show all existing backups
    all_backups = list_backups(cfg.backup_dir)
    print(f"\n  Total backups in '{cfg.backup_dir}': {len(all_backups)}")

    # List comprehension — show last 5 only
    recent = all_backups[-5:]
    for b in recent:
        print(f"    {b}")

    if len(all_backups) > 5:
        print(f"    ... and {len(all_backups) - 5} more")
    print()


def cmd_monitor(args) -> None:
    """devops monitor [-n N] [--parallel] — display system resource usage."""
    cfg = load_config()
    count = args.count or cfg.monitor_interval

    print(f"\n── System Monitor ({count} snapshots) ─────────────")

    if args.parallel:
        # Run monitor + log analysis simultaneously using threads
        print("  Running monitor + log analysis in parallel...\n")
        results = run_parallel(
            monitor_iterations=count,
            other_task=analyze_logs,
            task_kwargs={"log_path": cfg.log_path},
        )
        if results:
            print(format_analysis(results))
    else:
        # Simple sequential monitoring
        monitor_loop(interval=1, iterations=count)


def cmd_analyze_logs(args) -> None:
    """devops analyze-logs [file] — parse log file and show statistics."""
    cfg = load_config()
    log_path = args.file or cfg.log_path

    print(f"\n  Scanning: {log_path}")
    result = analyze_logs(log_path)
    print(format_analysis(result))
    print()


def cmd_env(args) -> None:
    """devops env — show environment variables from .env."""
    load_env()
    print(format_env())
    print()


def cmd_status(args) -> None:
    """devops status — project health check: config + system snapshot."""
    cfg  = load_config()
    snap = get_snapshot()

    print("\n── Project Status ────────────────────────")
    print(f"  Project  : {cfg.project_name}")
    print(f"  Log file : {cfg.log_path}")
    print(f"  Backups  : {cfg.backup_dir}")
    print(f"  Interval : {cfg.monitor_interval}s")
    print(f"  Level    : {cfg.log_level.value}")
    print(format_snapshot(snap))


# ══════════════════════════════════════════════════════════════════════════════
# ARGUMENT PARSER
# ══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Build and return the full argument parser with all subcommands."""

    parser = argparse.ArgumentParser(
        prog="devops",
        description="Local DevOps Automation CLI",
        epilog=(
            "Examples:\n"
            "  devops init\n"
            "  devops run pytest --verbose\n"
            "  devops monitor --count 5\n"
            "  devops backup data/config.yaml\n"
            "  devops analyze-logs\n"
            "  devops status\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global flags — work with any subcommand
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable DEBUG level logging"
    )

    # ── Subcommands ────────────────────────────────────────
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # init
    sub.add_parser(
        "init",
        help="Initialise project directories"
    )

    # run
    p_run = sub.add_parser(
        "run",
        help="Run an external command (pytest, git, docker...)"
    )
    p_run.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="Command and its arguments"
    )

    # backup
    p_backup = sub.add_parser(
        "backup",
        help="Backup a file with a timestamp"
    )
    p_backup.add_argument(
        "file",
        nargs="?",                        # optional — ? means 0 or 1
        help="File to backup (default: data/config.yaml)"
    )

    # monitor
    p_monitor = sub.add_parser(
        "monitor",
        help="Display live system CPU / RAM / Disk usage"
    )
    p_monitor.add_argument(
        "-n", "--count",
        type=int,
        help="Number of snapshots to take"
    )
    p_monitor.add_argument(
        "--parallel",
        action="store_true",
        help="Run log analysis in parallel with monitoring"
    )

    # analyze-logs
    p_logs = sub.add_parser(
        "analyze-logs",
        help="Parse log file and show ERROR / WARNING / INFO counts"
    )
    p_logs.add_argument(
        "file",
        nargs="?",
        help="Log file to analyze (default: from config.yaml)"
    )

    # env
    sub.add_parser(
        "env",
        help="Show environment variables from .env (secrets redacted)"
    )

    # status
    sub.add_parser(
        "status",
        help="Project health check — config + system snapshot"
    )

    return parser


# ══════════════════════════════════════════════════════════════════════════════
# DISPATCH TABLE
# Maps command name → handler function.
# Adding a new command = one new line here + one handler function.
# ══════════════════════════════════════════════════════════════════════════════

COMMANDS = {
    "init"         : cmd_init,
    "run"          : cmd_run,
    "backup"       : cmd_backup,
    "monitor"      : cmd_monitor,
    "analyze-logs" : cmd_analyze_logs,
    "env"          : cmd_env,
    "status"       : cmd_status,
}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    # ── Setup logging first — everything else may log ──────
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(level=log_level)

    # ── No command typed — show help ───────────────────────
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # ── Look up the handler in the dispatch table ──────────
    handler = COMMANDS.get(args.command)

    if handler is None:
        print(f"Unknown command: {args.command}")
        print("Run 'devops --help' to see available commands.")
        sys.exit(1)

    # ── Run the handler ────────────────────────────────────
    try:
        handler(args)

    except KeyboardInterrupt:
        # User pressed Ctrl+C — exit cleanly, no ugly traceback
        print("\n\nStopped by user.")
        sys.exit(0)

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)

    except Exception as e:
        # Log full traceback to file, show clean message in terminal
        logging.error(f"Fatal error: {e}")
        logging.debug(traceback.format_exc())
        print(f"\n  Error: {e}")
        print("  Run with --debug for full details.")
        sys.exit(1)


if __name__ == "__main__":
    main()