import time
import datetime
import sys
import json
import logging
from typing import Optional, Tuple

import pyautogui
import pydirectinput
from pywinauto import Application

# ==========================
# 🧭 Configuration
# ==========================

CONFIG_PATH = "config.json"

with open(CONFIG_PATH, "r") as config_file:
    CONFIG = json.load(config_file)

GEAR_IMAGE_PATH = CONFIG["image_paths"]["gear"]
EXIT_IMAGE_PATH = CONFIG["image_paths"]["exit"]
GEAR_ITEMS_TO_PURCHASE = CONFIG["gear_items_to_purchase"]
FIVE_MINUTES = 300  # seconds

# ==========================
# 🪵 Logging Setup
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
# 🛠 Utility Functions
# ==========================

def move_and_click(position: Tuple[int, int], dry_run: bool = False):
    pyautogui.moveTo(position)
    pydirectinput.moveRel(1, 0)
    pydirectinput.moveRel(-1, 0)
    if not dry_run:
        pyautogui.click()
    logger.debug(f"Clicked at {position} (dry_run={dry_run})")

def locate_and_click(image_path: str, description: str = "element", dry_run: bool = False) -> bool:
    for attempt in range(3):
        location = pyautogui.locateOnScreen(image_path, grayscale=True, confidence=0.8)
        if location:
            move_and_click(pyautogui.center(location), dry_run)
            return True
        time.sleep(2)
    logger.error(f"{description.capitalize()} not found after retries.")
    sys.exit(1)

def click_exit_button(dry_run: bool = False):
    locate_and_click(EXIT_IMAGE_PATH, "exit button", dry_run)
    time.sleep(0.5)

def within_same_5min_window(last_run: Optional[datetime.datetime]) -> bool:
    if not last_run:
        return False
    now = datetime.datetime.now()
    return (now - last_run).total_seconds() < FIVE_MINUTES and (now.minute // 5) == (last_run.minute // 5)

def wait_for_next_5min_window(last_run: Optional[datetime.datetime]):
    while within_same_5min_window(last_run):
        time.sleep(1)

# ==========================
# ⚙️ Gear Shop Automation
# ==========================

def purchase_item(item_pos: Tuple[int, int], button_pos: Tuple[int, int], times: int, dry_run: bool = False):
    move_and_click(item_pos, dry_run)
    time.sleep(0.5)
    for _ in range(times):
        move_and_click(button_pos, dry_run)
    move_and_click(item_pos, dry_run)

def gear_automation_purchase(dry_run: bool = False):
    scroll_per_item = -120
    item_pos = tuple(CONFIG["gear_shop"]["item_position"])
    button_pos = tuple(CONFIG["gear_shop"]["buy_button_position"])
    purchase_times = 3

    pydirectinput.press('e')
    time.sleep(3)

    if not locate_and_click(GEAR_IMAGE_PATH, "gear shop", dry_run):
        return

    time.sleep(3)
    pyautogui.scroll(-470)

    for i in range(GEAR_ITEMS_TO_PURCHASE):
        if i == 2:
            purchase_times = 2
        elif i == 3:
            scroll_per_item = -145
            item_pos = (974, 551)
            button_pos = (764, 700)
        elif i == 5:
            pyautogui.scroll(scroll_per_item)
            time.sleep(0.5)
            continue
        elif i == GEAR_ITEMS_TO_PURCHASE - 1:
            button_pos = (771, 730)

        purchase_item(item_pos, button_pos, purchase_times, dry_run)
        time.sleep(0.5)
        pyautogui.scroll(scroll_per_item)

    pyautogui.scroll(-600)
    time.sleep(0.5)
    purchase_item((967, 739), (778, 794), purchase_times, dry_run)
    pyautogui.scroll(2500)
    time.sleep(3)
    click_exit_button(dry_run)

def buy_egg(dry_run: bool = False):
    for _ in range(6):
        pydirectinput.press('a')

    pydirectinput.press('e')
    time.sleep(3)

    if not locate_and_click(GEAR_IMAGE_PATH, "gear shop", dry_run):
        return

    time.sleep(3)
    pyautogui.scroll(-400)

    for i in range(3):
        item_pos = (975, 583)
        button_pos = (845, 660)
        if i == 2:
            item_pos = (971, 747)
            button_pos = (833, 805)
        purchase_item(item_pos, button_pos, 1, dry_run)
        time.sleep(0.5)
        pyautogui.scroll(-100)

    pyautogui.scroll(700)
    time.sleep(3)
    click_exit_button(dry_run)
    for _ in range(6):
        pydirectinput.press('d')

# ==========================
# 🔁 Main Automation Loop
# ==========================

def automation_cycle(dry_run: bool = False):
    logger.info("Starting automation cycle...")
    gear_automation_purchase(dry_run)
    buy_egg(dry_run)

def focus_roblox_window() -> bool:
    try:
        app = Application(backend="uia").connect(title_re=".*Roblox.*")
        app.top_window().set_focus()
        logger.info("Roblox window focused.")
        return True
    except Exception as e:
        logger.error(f"Could not focus Roblox window: {e}")
        return False

def main(dry_run: bool = False):
    logger.info("BOT INITIALIZED")
    last_run = None
    run_count = 0

    try:
        while True:
            if not within_same_5min_window(last_run):
                if focus_roblox_window():
                    automation_cycle(dry_run)
                    last_run = datetime.datetime.now()
                    run_count += 1
                    logger.info(f"Cycle complete. Total runs: {run_count}")
            else:
                wait_for_next_5min_window(last_run)
    except KeyboardInterrupt:
        logger.info(f"Bot terminated by user. Total cycles: {run_count}")
        sys.exit(0)

if __name__ == '__main__':
    main(dry_run=False)
