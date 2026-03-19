"""
core/system_monitor.py
-----------------------
Reads real CPU, RAM, Disk stats and runs monitoring loops.
Concepts: psutil, datetime, threading, daemon threads,
          shared state between threads, time.sleep
"""

import psutil
import threading
import time
import logging
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


# ── Single Snapshot ────────────────────────────────────────────────────────────

def get_snapshot() -> dict:
    """
    Collect one system snapshot right now.
    cpu_percent(interval=1) measures over 1 second — more accurate
    than interval=None which returns usage since last call.
    """
    return {
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu"       : psutil.cpu_percent(interval=1),
        "ram"       : psutil.virtual_memory().percent,
        "disk"      : psutil.disk_usage("/").percent,
        "processes" : len(psutil.pids()),
    }


# ── Formatter ─────────────────────────────────────────────────────────────────

def format_snapshot(snap: dict) -> str:
    """Format a snapshot dict into a readable display block."""
    return (
        f"\n── System Monitor ────────────────────\n"
        f"  Time       : {snap['timestamp']}\n"
        f"  CPU        : {snap['cpu']}%\n"
        f"  RAM        : {snap['ram']}%\n"
        f"  Disk       : {snap['disk']}%\n"
        f"  Processes  : {snap['processes']}\n"
    )


# ── Monitor Loop ───────────────────────────────────────────────────────────────

def monitor_loop(
    interval: int = 5,
    iterations: int = 3,
    callback: Optional[Callable[[dict], None]] = None,
) -> None:
    """
    Take repeated system snapshots.

    Args:
        interval   : seconds to wait between snapshots
        iterations : how many snapshots to take (0 = run forever)
        callback   : optional function to call with each snapshot dict
                     if None, prints the formatted snapshot to terminal
    """
    logger.info(f"Monitor started — {iterations} snapshots, {interval}s apart")
    count = 0

    while True:
        snap = get_snapshot()
        logger.debug(f"Snapshot: CPU={snap['cpu']}% RAM={snap['ram']}%")

        # Either call the custom callback or just print
        if callback:
            callback(snap)
        else:
            print(format_snapshot(snap))

        count += 1

        # Stop if we've hit our target number of iterations
        # iterations=0 means run forever
        if iterations and count >= iterations:
            break

        time.sleep(interval)

    logger.info("Monitor loop finished")


# ── Background Thread ──────────────────────────────────────────────────────────

def start_monitor_thread(
    interval: int = 5,
    iterations: int = 3,
) -> threading.Thread:
    """
    Run monitor_loop in a background daemon thread.

    daemon=True means this thread dies automatically
    when the main program exits — no hanging.

    Returns the thread so caller can .join() it if needed.
    """
    t = threading.Thread(
        target=monitor_loop,
        kwargs={
            "interval"  : interval,
            "iterations": iterations,
        },
        daemon=True,
    )
    t.start()
    logger.info(f"Monitor thread started (id={t.ident})")
    return t


# ── Parallel: Monitor + Any Other Task ────────────────────────────────────────

def run_parallel(
    monitor_iterations: int = 3,
    other_task: Optional[Callable] = None,
    task_kwargs: Optional[dict] = None,
) -> Optional[dict]:
    """
    Run system monitoring alongside another task simultaneously.

    Args:
        monitor_iterations : snapshots to take
        other_task         : any callable to run in parallel
        task_kwargs        : keyword args to pass to other_task

    Returns:
        result dict from other_task if it writes to a shared dict,
        else None
    """
    task_kwargs = task_kwargs or {}
    results: dict = {}

    # Wrap the other task so it stores results in shared dict
    def run_other():
        if other_task:
            output = other_task(**task_kwargs)
            if isinstance(output, dict):
                results.update(output)

    # Two threads — both start at the same time
    t_monitor = threading.Thread(
        target=monitor_loop,
        kwargs={"interval": 1, "iterations": monitor_iterations},
        daemon=True,
    )
    t_other = threading.Thread(target=run_other, daemon=True)

    logger.info("Starting parallel tasks")
    t_monitor.start()
    t_other.start()

    # Wait for BOTH to finish before returning
    t_monitor.join()
    t_other.join()
    logger.info("Parallel tasks complete")

    return results if results else None