import time
import datetime
import sys
import json
import logging
from typing import Optional, Tuple

import pyautogui
import pydirectinput
from pywinauto import Application
import requests

# ==========================
# 🧭 Configuration
# ==========================

CONFIG_PATH = "config.json"

with open(CONFIG_PATH, "r") as config_file:
    CONFIG = json.load(config_file)

GEAR_IMAGE_PATH = CONFIG["image_paths"]["gear"]
EXIT_IMAGE_PATH = CONFIG["image_paths"]["exit"]
GEAR_ITEMS_TO_PURCHASE = CONFIG["gear_items_to_purchase"]
DISCORD_HOOK_URL = CONFIG["discord_hook_url"]
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

def send_discord_notification(message: str):
    """
    Sends a notification message to a Discord channel using a webhook.

    Args:
        message (str): The message to send to the Discord channel.
    """
    if not DISCORD_HOOK_URL:
        logger.warning("Discord webhook URL is not set. Skipping notification.")
        return

    try:
        response = requests.post(DISCORD_HOOK_URL, json={"content": message})
        response.raise_for_status()
        logger.info("Discord notification sent successfully.")
    except requests.RequestException as e:
        logger.error(f"Failed to send Discord notification: {e}")

def elapsed_time(start_time: float):
    """Calculates and logs the elapsed time since start_time."""
    end_time = time.time()
    elapsed_seconds = int(end_time - start_time)
    hours = elapsed_seconds // 3600
    minutes = (elapsed_seconds % 3600) // 60
    seconds = elapsed_seconds % 60
    logger.info(f"Ran for: {hours:02}:{minutes:02}:{seconds:02} h:m:s")

def move_and_click(position: Tuple[int, int]):
    """
    Move the mouse cursor to a specified screen position and simulate a click.

    Args:
        position (Tuple[int, int]): The (x, y) coordinates on the screen where the click should occur.
    """
    pyautogui.moveTo(position)
    pydirectinput.moveRel(1, 0)
    pydirectinput.moveRel(-1, 0)
    pyautogui.click()
    logger.debug(f"Clicked at {position}")

def locate_and_click(image_path: str, description: str = "element") -> bool:
    """
    Attempt to locate an image on the screen and perform a click on its center if found.

    Args:
        image_path (str): Path to the image to locate on screen.
        description (str): Text description of the element being located (for logging).

    Returns:
        bool: True if the image was found and clicked, otherwise exits the program.
    """
    retry = 5
    for attempt in range(retry):
        try:
            location = pyautogui.locateOnScreen(image_path, grayscale=True, confidence=0.8)
            if location:
                move_and_click(pyautogui.center(location))
                return True
        except pyautogui.ImageNotFoundException:
            logger.warning(f"{description.capitalize()} not found on attempt {attempt + 1}. Retrying...")
        time.sleep(2)
    logger.error(f"{description.capitalize()} not found after {attempt + 1} retries.")
    logger.error("Exiting program.")
    sys.exit(1)

def click_exit_button():
    """Finds and clicks the exit button in the UI."""
    locate_and_click(EXIT_IMAGE_PATH, "exit button")
    time.sleep(0.5)

def within_same_5min_window(last_run: Optional[datetime.datetime]) -> bool:
    """Checks if the current time is within the same 5-minute window as the last run."""
    if not last_run:
        return False
    now = datetime.datetime.now()
    return (now - last_run).total_seconds() < FIVE_MINUTES and (now.minute // 5) == (last_run.minute // 5)

def wait_for_next_5min_window(last_run: Optional[datetime.datetime]):
    """Waits until a new 5-minute window has started."""
    while within_same_5min_window(last_run):
        time.sleep(1)

# ==========================
# ⚙️ Gear Shop Automation
# ==========================

def purchase_item(item_pos: Tuple[int, int], button_pos: Tuple[int, int], times: int):
    """
    Clicks on a gear item and its corresponding buy button a specified number of times.

    Args:
        item_pos (Tuple[int, int]): Coordinates of the gear item.
        button_pos (Tuple[int, int]): Coordinates of the buy button.
        times (int): Number of times to click the buy button.
    """
    move_and_click(item_pos)
    time.sleep(0.5)
    for _ in range(times):
        move_and_click(button_pos)
    move_and_click(item_pos)

def gear_automation_purchase():
    """Automates purchasing of gear items from the in-game shop."""
    scroll_per_item = -120
    item_pos = tuple(CONFIG["gear_shop"]["item_position"])
    button_pos = tuple(CONFIG["gear_shop"]["buy_button_position"])
    purchase_times = 3

    pydirectinput.press('e')
    time.sleep(3)

    if not locate_and_click(GEAR_IMAGE_PATH, "gear shop"):
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

        purchase_item(item_pos, button_pos, purchase_times)
        time.sleep(0.5)
        pyautogui.scroll(scroll_per_item)

    pyautogui.scroll(-600)
    time.sleep(0.5)
    purchase_item((967, 739), (778, 794), purchase_times)
    pyautogui.scroll(2500)
    time.sleep(3)
    click_exit_button()

def buy_egg():
    """Automates the process of buying eggs in the game."""
    for _ in range(6):
        pydirectinput.press('a')

    pydirectinput.press('e')
    time.sleep(3)

    if not locate_and_click(GEAR_IMAGE_PATH, "gear shop"):
        return

    time.sleep(3)
    pyautogui.scroll(-400)

    for i in range(3):
        item_pos = (975, 583)
        button_pos = (845, 660)
        if i == 2:
            item_pos = (971, 747)
            button_pos = (833, 805)
        purchase_item(item_pos, button_pos, 1)
        time.sleep(0.5)
        pyautogui.scroll(-100)

    pyautogui.scroll(700)
    time.sleep(3)
    click_exit_button()
    for _ in range(6):
        pydirectinput.press('d')

# ==========================
# 🔁 Main Automation Loop
# ==========================

def automation_cycle():
    """Executes one full automation cycle for gear and egg purchasing."""
    logger.info("Starting automation cycle...")
    gear_automation_purchase()
    buy_egg()

def focus_roblox_window() -> bool:
    """Attempts to focus the Roblox game window."""
    try:
        app = Application(backend="uia").connect(title_re=".*Roblox.*")
        app.top_window().set_focus()
        logger.info("Roblox window focused.")
        return True
    except Exception as e:
        logger.error(f"Could not focus Roblox window: {e}")
        return False

def main():
    """Main entry point for the bot, runs automation loop continuously."""
    logger.info("BOT INITIALIZED")
    last_run = None
    run_count = 0
    start_time = time.time()

    try:
        while True:
            if not within_same_5min_window(last_run):
                if focus_roblox_window():
                    automation_cycle()
                    last_run = datetime.datetime.now()
                    run_count += 1
                    logger.info(f"Cycle complete. Total runs: {run_count}")
            else:
                wait_for_next_5min_window(last_run)
    except KeyboardInterrupt:
        logger.info(f"Bot terminated by user. Total cycles: {run_count}")
        elapsed_time(start_time)
        sys.exit(0)

if __name__ == '__main__':
    main()
