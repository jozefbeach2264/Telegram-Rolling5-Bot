# rolling5/telegram_bot.py
from telegram import Update
from telegram.ext import Application, ContextTypes
# This is your fix: import CommandHandler with an alias to avoid name collision
from telegram.ext import CommandHandler as TelegramCommandHandler
from command_handler import CommandHandler

class TelegramBot:
    def __init__(self, config, command_handler: CommandHandler):
        """
        Keeps the __init__ method clean. Only stores configuration.
        No library logic is run here to prevent import-time crashes.
        """
        self.config = config
        self.command_handler = command_handler
        self.application = None  # Initialize as None

    # --- Lifecycle Management Methods ---

    async def initialize(self):
        """
        Builds the bot application and registers all handlers.
        This method is called from the FastAPI lifespan event,
        ensuring the event loop is running.
        """
        print("INFO: Initializing Telegram Bot...")
        self.application = Application.builder().token(self.config.telegram_bot_token).build()

        # Register command handlers safely inside the async context using the alias
        self.application.add_handler(TelegramCommandHandler("start", self.start))
        self.application.add_handler(TelegramCommandHandler("status", self.status))

        await self.application.initialize()
        print("INFO: Bot Initialized.")

    async def start_polling(self):
        """Starts the polling process in a non-blocking way."""
        print("INFO: Starting bot polling...")
        await self.application.start()
        await self.application.updater.start_polling()
        print("INFO: Bot polling started.")

    async def stop_polling(self):
        """Stops the polling process."""
        print("INFO: Stopping bot polling...")
        if self.application and self.application.updater and self.application.updater.is_running:
            await self.application.updater.stop()
        print("INFO: Bot polling stopped.")

    async def shutdown(self):
        """Shuts down the bot application gracefully."""
        print("INFO: Shutting down Telegram Bot...")
        if self.application:
            await self.application.shutdown()
        print("INFO: Bot shut down.")

    # --- Command Handlers ---

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await self.command_handler.handle_start(update.effective_chat.id)
        await update.message.reply_text(response)

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await self.command_handler.handle_status(update.effective_chat.id)
        await update.message.reply_html(response)
