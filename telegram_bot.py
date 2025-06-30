import logging
from functools import wraps
from telegram import Update, constants
from telegram.ext import Application, ContextTypes, CommandHandler as TelegramCommandHandler

# ... (imports and decorator remain the same)

class TelegramBot:
    # ... (__init__ and _setup_handlers remain the same)
    
    async def start_polling(self):
        # ... (logic remains the same)

    async def shutdown(self):
        # ... (logic remains the same)

    # --- NEW Method to send messages directly ---
    async def send_message_to_user(self, message: str):
        """Sends a message directly to the authorized user."""
        if not self.config.authorized_user_id:
            logger.warning("Cannot send direct message, AUTHORIZED_USER_ID not set.")
            return

        try:
            await self.application.bot.send_message(
                chat_id=self.config.authorized_user_id,
                text=message,
                parse_mode=constants.ParseMode.HTML
            )
            logger.info("Successfully sent direct message to authorized user.")
        except Exception as e:
            logger.error(f"Failed to send direct message: {e}")

    # --- Command Handler Methods ---
    # ... (all command handlers like start, status, trade, etc. remain the same)
