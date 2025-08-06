import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_HOOK_URL = os.getenv("DISCORD_HOOK_URL")

logger = logging.getLogger(__name__)

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
