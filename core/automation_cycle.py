import logging
import threading
import pyautogui
import pydirectinput

from core.actions import move_and_click, click_exit_button, locate_and_click
from core.discord import send_discord_notification
from core.utils import safe_sleep

from config import CONFIG 
from data.items import items

logger = logging.getLogger(__name__)

ONE_IMAGE_PATH = CONFIG["image_paths"]["gear"]
GEAR_NO_STOCK_IMAGE_PATH = CONFIG["image_paths"]["no-stock"]
EGG_NO_STOCK_IMAGE_PATH = CONFIG["image_paths"]["egg-no-stock"]

# ==========================
# Purchasing Automation
# ==========================

def purchase_item(item_pos: tuple[int, int], button_pos: tuple[int, int], times: int, item: str, shop: str, terminate_flag: threading.Event) -> None:
    always_in_stock = []
    if shop == "gear":
        always_in_stock = CONFIG.get("always_in_stock_gear")
    elif shop == "egg":
        always_in_stock = CONFIG.get("always_in_stock_egg")
        
    if terminate_flag.is_set():
        logger.info("Terminate flag set before purchase_item. Exiting.")
        return

    move_and_click(item_pos)
    safe_sleep(1, terminate_flag)

    try:
        if shop == "gear":
            is_no_stock_showing = pyautogui.locateOnScreen(GEAR_NO_STOCK_IMAGE_PATH, grayscale=True, confidence=0.8)
        elif shop == "egg":
            is_no_stock_showing = pyautogui.locateOnScreen(EGG_NO_STOCK_IMAGE_PATH, grayscale=True, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        # Send discord notification if item is in stock
        if item not in always_in_stock:
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
    safe_sleep(2, terminate_flag)

    if not locate_and_click(ONE_IMAGE_PATH, "gear shop", terminate_flag):
        return

    safe_sleep(2, terminate_flag)

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
        if i == len(gear_items) - 3:
            item_pos = (962, 564)
            button_pos = (766, 722)
        if i == len(gear_items) - 2:
            item_pos = (973, 622)
            button_pos = (760, 792)
        if i == num_of_gears_to_purchase - 1:
            item_pos = (970, 758)
            button_pos = (766, 814)

        if i in gears_to_purchase:
            purchase_item(item_pos, button_pos, purchase_times, gear_items[i], "gear", terminate_flag)
            click += 1
            safe_sleep(.5, terminate_flag)

        pyautogui.scroll(scroll_per_item)
        safe_sleep(.5, terminate_flag)

    pyautogui.scroll(3000)
    safe_sleep(2, terminate_flag)
    click_exit_button(terminate_flag)

# ==========================
# Egg Shop Automation
# ==========================

def egg_automation_purchase(eggs_to_purchase: list[int], terminate_flag: threading.Event) -> None:
    scroll_per_item = -160
    item_pos = tuple(CONFIG["egg_shop"]["item_position"])
    button_pos = tuple(CONFIG["egg_shop"]["buy_button_position"])
    purchase_times = 3
    egg_items = items["egg"]
    num_of_eggs_to_purchase = len(egg_items)

    pydirectinput.press('e')
    safe_sleep(3, terminate_flag)

    if not locate_and_click(ONE_IMAGE_PATH, "egg shop", terminate_flag):
        return

    safe_sleep(3, terminate_flag)

    click = 0

    for i in range(num_of_eggs_to_purchase):
        if terminate_flag.is_set():
            logger.info("Terminate flag set during gear purchase loop.")
            return
        
        if click == len(eggs_to_purchase):
            logger.info("All eggs to purchase have been processed.")
            break

        if i == len(egg_items) - 2:
            item_pos = (963, 542)
            button_pos = (833, 685)
        if i == num_of_eggs_to_purchase - 1:
            item_pos = (985, 759)
            button_pos = (826, 807)

        if i in eggs_to_purchase:
            purchase_item(item_pos, button_pos, purchase_times, egg_items[i], "egg", terminate_flag)
            click += 1
            safe_sleep(1, terminate_flag)

        pyautogui.scroll(scroll_per_item)
        safe_sleep(1, terminate_flag)

    pyautogui.scroll(1000)
    safe_sleep(3, terminate_flag)
    click_exit_button(terminate_flag)

def automation_cycle(gear_selected_keys: list[int], egg_selected_keys: list[int], terminate_flag: threading.Event) -> None:
    if gear_selected_keys and egg_selected_keys:
        gear_automation_purchase(gear_selected_keys, terminate_flag)

        # Move to the egg shop
        for _ in range(5):
            pydirectinput.press('a')
        egg_automation_purchase(egg_selected_keys, terminate_flag)

        # Move back to the gear shop
        for _ in range(5):
            pydirectinput.press('d')
    elif gear_selected_keys:
        gear_automation_purchase(gear_selected_keys, terminate_flag)
    elif egg_selected_keys:
        egg_automation_purchase(egg_selected_keys, terminate_flag)

    