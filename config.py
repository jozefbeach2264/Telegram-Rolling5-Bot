# TelegramBot/config.py
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
        # The /status URL for TradingCore
        self.core_status_url = os.getenv("CORE_STATUS_URL")
        # The /status URL for NeuroSync
        self.neurosync_status_url = os.getenv("NEUROSYNC_STATUS_URL")
