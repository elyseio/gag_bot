import sys
import time
import logging
import threading
import datetime

from core.utils import (
    within_same_5min_window,
    wait_for_next_5min_window,
    focus_roblox_window,
    elapsed_time,
)
from core.automation_cycle import automation_cycle

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==========================
# Main Bot Loop
# ==========================

def run_bot(gear_selected_keys: list[int], egg_selected_keys: list[int], terminate_flag: threading.Event) -> None:
    logger.info("BOT INITIALIZED")
    last_run = None
    run_count = 0
    start_time = time.time()
    if gear_selected_keys and egg_selected_keys:
        logger.info("Purchasing both gears and eggs.")
    elif gear_selected_keys:
        logger.info("Purchasing gears only.")
    elif egg_selected_keys:
        logger.info("Purchasing eggs only.")
    logger.info("Starting automation cycle...")

    try:
        while not terminate_flag.is_set():
            if not within_same_5min_window(last_run):
                if focus_roblox_window(terminate_flag):
                    automation_cycle(gear_selected_keys, egg_selected_keys, terminate_flag)
                    last_run = datetime.datetime.now()
                    run_count += 1
                    logger.info(f"Cycle complete. Total runs: {run_count}")
            else:
                wait_for_next_5min_window(last_run, terminate_flag)
    except KeyboardInterrupt:
        logger.info("Bot manually interrupted.")
    finally:
        logger.info(f"Bot gracefully terminated. Total cycles: {run_count}")
        elapsed_time(start_time)
