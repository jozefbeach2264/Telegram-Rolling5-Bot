# rolling5/telegram_bot.py
import logging
from telegram import Update
from telegram.ext import Application, ContextTypes
from telegram.ext import CommandHandler as TelegramCommandHandler
from telegram.error import NetworkError # <-- Import the specific error
from command_handler import CommandHandler
from config import Config

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, config: Config, command_handler: CommandHandler):
        self.config = config
        self.command_handler = command_handler
        self.application = None

    async def initialize(self):
        """Builds and initializes the bot application and handlers."""
        logger.info("Initializing Telegram Bot application...")
        self.application = Application.builder().token(self.config.telegram_bot_token).build()
        self.application.add_handler(TelegramCommandHandler("start", self.start))
        self.application.add_handler(TelegramCommandHandler("status", self.status))
        self.application.add_handler(TelegramCommandHandler("trade", self.trade))
        await self.application.initialize()
        logger.info("Telegram Bot initialized.")

    async def start_polling(self):
        """Starts the polling process."""
        if self.application:
            logger.info("Starting Telegram Bot polling...")
            await self.application.start()
            await self.application.updater.start_polling()

    async def shutdown(self):
        """Stops the application gracefully and then shuts it down, handling network errors."""
        if self.application:
            try:
                # First, stop all running components
                if self.application.updater and self.application.updater.is_running:
                    logger.info("Stopping bot polling...")
                    await self.application.updater.stop()
                
                logger.info("Shutting down Telegram application...")
                await self.application.shutdown()
                
                logger.info("Telegram Bot shut down successfully.")
            except NetworkError as e:
                # If a network error occurs during shutdown, log it gracefully
                logger.warning(f"Shutdown failed due to a network error: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred during bot shutdown: {e}")

    # --- Command Handlers ---
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await self.command_handler.handle_start(update.effective_chat.id)
        await update.message.reply_text(response)

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await self.command_handler.handle_status(update.effective_chat.id)
        await update.message.reply_html(response)
    
    async def trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        strategy = context.args[0].lower() if context.args else ""
        response = await self.command_handler.handle_trade_command(strategy, update.effective_chat.id)
        await update.message.reply_html(response)
