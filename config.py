# rolling5/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Manages all configuration for the Rolling5 Telegram Bot."""
    def __init__(self):
        # Telegram Bot Credentials
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        # URLs for backend services
        self.neuro_health_url = os.getenv("NEUROSYNC_STATUS_URL")
        self.core_status_url = os.getenv("CORE_STATUS_URL")
        self.core_validate_url = os.getenv("CORE_VALIDATE_URL")

        if not self.telegram_bot_token:
            raise ValueError("FATAL: TELEGRAM_BOT_TOKEN secret is not set.")
