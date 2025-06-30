import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Rolling5Config:
    """
    Manages all configuration for the Rolling5 Telegram Bot application.
    """
    def __init__(self):
        logger.info("Initializing Rolling5 configuration...")

        # Telegram Bot Token from secrets
        self.telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_bot_token:
            raise ValueError("FATAL: TELEGRAM_BOT_TOKEN secret is not set.")

        # The single authorized user ID for this bot
        self.authorized_user_id: int = int(os.getenv("AUTHORIZED_USER_ID", 0))
        if self.authorized_user_id == 0:
            logger.warning("AUTHORIZED_USER_ID is not set. The bot will respond to all users.")

        # URLs for backend services that the bot will communicate with
        self.neuro_health_url: str = os.getenv("NEUROSYNC_STATUS_URL")
        self.core_status_url: str = os.getenv("CORE_STATUS_URL")
        self.core_validate_url: str = os.getenv("CORE_VALIDATE_URL")
        
        logger.info("Rolling5 configuration loaded.")

# Instantiate a global config object for easy access
config = Rolling5Config()
