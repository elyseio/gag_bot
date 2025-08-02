import os
from dotenv import load_dotenv
import time
import datetime
import sys
import json
import logging
import threading
from typing import Optional, Tuple

import pyautogui
import pydirectinput
from pywinauto import Application
import requests
import FreeSimpleGUI as sg

from items import items

# ==========================
# Configuration
# ==========================

load_dotenv()
DISCORD_HOOK_URL = os.getenv("DISCORD_HOOK_URL")

CONFIG_PATH = "config.json"

with open(CONFIG_PATH, "r") as config_file:
    CONFIG = json.load(config_file)

GEAR_IMAGE_PATH = CONFIG["image_paths"]["gear"]
EXIT_IMAGE_PATH = CONFIG["image_paths"]["exit"]
NO_STOCK_IMAGE_PATH = CONFIG["image_paths"]["no-stock"]
FIVE_MINUTES = 300  # seconds

# ==========================
# Logging Setup
# ==========================

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

def focus_roblox_window() -> bool:
    try:
        app = Application(backend="uia").connect(title_re=".*Roblox.*")
        app.top_window().set_focus()
        logger.info("Roblox window focused.")
        return True
    except Exception as e:
        for _ in range(10):
            logger.error("Roblox window not found. Retrying in 1 second...")
            time.sleep(1)
        logger.error(f"Could not focus Roblox window: {e}")
        sys.exit(1)
        return False

def send_discord_notification(message: str, item: str) -> None:
    if not DISCORD_HOOK_URL:
        logger.warning("Discord webhook URL is not set. Skipping notification.")
        return
    try:
        response = requests.post(DISCORD_HOOK_URL, json={"content": message})
        response.raise_for_status()
        logger.info(f"Discord notification sent successfully: {item}")
    except requests.RequestException as e:
        logger.error(f"Failed to send Discord notification: {e}")

def move_and_click(position: Tuple[int, int]) -> None:
    pyautogui.moveTo(position)
    pydirectinput.moveRel(1, 0)
    pydirectinput.moveRel(-1, 0)
    pyautogui.click()
    logger.debug(f"Clicked at {position}")

def locate_and_click(image_path: str, description: str = "element", terminate_flag: Optional[threading.Event] = None) -> bool:
    retry = 5
    for attempt in range(retry):
        if terminate_flag and terminate_flag.is_set():
            logger.info("Termination flag set during locate_and_click. Exiting early.")
            return False
        location = pyautogui.locateOnScreen(image_path, grayscale=True, confidence=0.8)
        if location:
            move_and_click(pyautogui.center(location))
            return True
        logger.warning(f"{description.capitalize()} not found on attempt {attempt + 1}. Retrying...")
        safe_sleep(2, terminate_flag)

    logger.error(f"{description.capitalize()} not found after {retry} retries.")
    if terminate_flag:
        terminate_flag.set()
    return False

def click_exit_button(terminate_flag: Optional[threading.Event] = None) -> None:
    locate_and_click(EXIT_IMAGE_PATH, "exit button", terminate_flag)
    safe_sleep(0.5, terminate_flag)

# ==========================
# Purchasing Automation
# ==========================

def purchase_item(item_pos: Tuple[int, int], button_pos: Tuple[int, int], times: int, item: str, shop: str, terminate_flag: threading.Event) -> None:
    if terminate_flag.is_set():
        logger.info("Terminate flag set before purchase_item. Exiting.")
        return

    move_and_click(item_pos)
    safe_sleep(1, terminate_flag)

    try:
        is_no_stock_showing = pyautogui.locateOnScreen(NO_STOCK_IMAGE_PATH, grayscale=True, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        send_discord_notification(f"{item} is in stock!", item)
        safe_sleep(0.5, terminate_flag)
    else:
        move_and_click(item_pos)
        return

    for _ in range(times):
        if terminate_flag.is_set():
            logger.info("Terminate flag set during purchase loop. Exiting.")
            return
        move_and_click(button_pos)
        safe_sleep(0.1, terminate_flag)
    move_and_click(item_pos)

# ==========================
# Gear Shop Automation
# ==========================

def gear_automation_purchase(gears_to_purchase: list[int], terminate_flag: threading.Event) -> None:
    scroll_per_item = -160
    item_pos = tuple(CONFIG["gear_shop"]["item_position"])
    button_pos = tuple(CONFIG["gear_shop"]["buy_button_position"])
    purchase_times = 3
    gear_items = items["gear"]
    num_of_gears_to_purchase = len(gear_items)

    pydirectinput.press('e')
    safe_sleep(3, terminate_flag)

    if not locate_and_click(GEAR_IMAGE_PATH, "gear shop", terminate_flag):
        return

    safe_sleep(3, terminate_flag)

    click = 0

    for i in range(num_of_gears_to_purchase):
        if terminate_flag.is_set():
            logger.info("Terminate flag set during gear purchase loop.")
            return
        
        if click == len(gears_to_purchase):
            logger.info("All gears to purchase have been processed.")
            break

        if i == 6:
            item_pos = (971, 503)
            button_pos = (770, 724)
        if i == 10:
            item_pos = (971, 503)
            button_pos = (775, 768)
        if i == len(gear_items) - 2:
            item_pos = (973, 622)
            button_pos = (760, 792)
        if i == num_of_gears_to_purchase - 1:
            item_pos = (970, 758)
            button_pos = (766, 814)

        if i in gears_to_purchase:
            purchase_item(item_pos, button_pos, purchase_times, gear_items[i], "gear", terminate_flag)
            click += 1
            safe_sleep(1, terminate_flag)

        pyautogui.scroll(scroll_per_item)
        safe_sleep(1, terminate_flag)

    pyautogui.scroll(3000)
    safe_sleep(3, terminate_flag)
    click_exit_button(terminate_flag)

def automation_cycle(selected_keys: list[int], terminate_flag: threading.Event) -> None:
    logger.info("Starting automation cycle...")
    gear_automation_purchase(selected_keys, terminate_flag)

# ==========================
# Main Function
# ==========================

def run_bot(selected_keys: list[int], terminate_flag: threading.Event) -> None:
    logger.info("BOT INITIALIZED")
    last_run = None
    run_count = 0
    start_time = time.time()

    try:
        while not terminate_flag.is_set():
            if not within_same_5min_window(last_run):
                if focus_roblox_window():
                    automation_cycle(selected_keys, terminate_flag)
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
