import pyautogui
import pydirectinput
import logging
import threading
from typing import Optional, Tuple

from config import CONFIG
from core.utils import safe_sleep

logger = logging.getLogger(__name__)
EXIT_IMAGE_PATH = CONFIG["image_paths"]["exit"]

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
        try:
            location = pyautogui.locateOnScreen(image_path, grayscale=True, confidence=0.8)
            if location:
                move_and_click(pyautogui.center(location))
                return True
        except pyautogui.ImageNotFoundException:
            logger.warning(f"{description.capitalize()} not found on attempt {attempt + 1}. Retrying...")
            safe_sleep(1, terminate_flag)

    logger.error(f"{description.capitalize()} not found after {retry} retries.")
    if terminate_flag:
        terminate_flag.set()
    return False

def click_exit_button(terminate_flag: Optional[threading.Event] = None) -> None:
    locate_and_click(EXIT_IMAGE_PATH, "exit button", terminate_flag)
    safe_sleep(0.5, terminate_flag)
