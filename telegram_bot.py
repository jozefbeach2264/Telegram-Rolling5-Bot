import logging
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler as TelegramCommandHandler
from telegram.error import NetworkError
from command_handler import CommandHandler
from config import Config

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, config: Config, command_handler: CommandHandler):
        self.config = config
        self.command_handler = command_handler
        self.application = None

    async def initialize(self):
        logger.info("Initializing Telegram Bot application...")
        try:
            self.application = Application.builder().token(self.config.telegram_bot_token).build()
            self.application.add_handler(TelegramCommandHandler("start", self.start))
            self.application.add_handler(TelegramCommandHandler("status", self.status))
            self.application.add_handler(TelegramCommandHandler("trade", self.trade))
            await self.application.initialize()
            logger.info("Telegram Bot initialized.")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    async def start_polling(self):
        logger.info("Starting Telegram Bot polling...")
        if self.application:
            try:
                await self.application.start_polling()
                logger.info("Polling started.")
            except NetworkError as e:
                logger.error(f"Polling failed: {e}")
                raise

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text(await self.command_handler.handle_start(update.effective_user.id))
        except Exception as e:
            logger.error(f"Start command failed: {e}")
            await update.message.reply_text("Error processing /start.")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            response = await self.command_handler.handle_status(update.effective_user.id)
            await update.message.reply_text(response, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Status command failed: {e}")
            await update.message.reply_text("Error retrieving status.")

    async def trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            strategy = " ".join(context.args) if context.args else ""
            await update.message.reply_text(await self.command_handler.handle_trade_command(strategy, update.effective_user.id))
        except Exception as e:
            logger.error(f"Trade command failed: {e}")
            await update.message.reply_text("Error processing /trade.")

    async def shutdown(self):
        logger.info("Shutting down Telegram Bot...")
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram Bot shutdown complete.")
            except Exception as e:
                logger.error(f"Shutdown failed: {e}")
                raise