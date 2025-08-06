# core/utils.py
import time
import datetime
import logging
import threading
from pywinauto import Application
from typing import Optional

logger = logging.getLogger(__name__)
FIVE_MINUTES = 300

# ==========================
# Utility Functions
# ==========================

def safe_sleep(seconds: float, terminate_flag: Optional[threading.Event] = None) -> None:
    interval = 0.1
    elapsed = 0.0
    while elapsed < seconds:
        if terminate_flag and terminate_flag.is_set():
            break
        time.sleep(interval)
        elapsed += interval

def within_same_5min_window(last_run: Optional[datetime.datetime]) -> bool:
    if not last_run:
        return False
    now = datetime.datetime.now()
    return (now - last_run).total_seconds() < FIVE_MINUTES and (now.minute // 5) == (last_run.minute // 5)

def wait_for_next_5min_window(last_run: Optional[datetime.datetime], terminate_flag: threading.Event) -> None:
    while within_same_5min_window(last_run):
        if terminate_flag.is_set():
            break
        safe_sleep(1, terminate_flag)

def elapsed_time(start_time: float) -> None:
    end_time = time.time()
    elapsed_seconds = int(end_time - start_time)
    hours = elapsed_seconds // 3600
    minutes = (elapsed_seconds % 3600) // 60
    seconds = elapsed_seconds % 60
    logger.info(f"Ran for: {hours:02}:{minutes:02}:{seconds:02} h:m:s")

def focus_roblox_window(terminate_flag: Optional[threading.Event] = None) -> bool:
    try:
        app = Application(backend="uia").connect(title_re=".*Roblox.*")
        app.top_window().set_focus()
        logger.info("Roblox window focused.")
        return True
    except Exception as e:
        for attempt in range(10):
            if terminate_flag and terminate_flag.is_set():
                logger.info("Termination flag set during Roblox window focus. Exiting.")
                return False
            logger.error(f"Roblox window not found (attempt {attempt + 1}/10). Retrying in 1 second...")
            time.sleep(1)

        logger.error(f"Could not focus Roblox window after 10 attempts: {e}")
        if terminate_flag:
            terminate_flag.set()
        return False