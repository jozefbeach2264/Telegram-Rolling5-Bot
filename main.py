import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import Config
from core_api_client import CoreApiClient
from command_handler import CommandHandler
from telegram_bot import TelegramBot

# --- Application Setup ---
config = Config()
api_client = CoreApiClient(config)
command_handler = CommandHandler(api_client)
telegram_bot = TelegramBot(config, command_handler)

# The lifespan context manager is the modern way to handle startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run on startup ---
    await telegram_bot.initialize()
    await telegram_bot.start_polling()

    yield # The application is now running

    # --- Code to run on shutdown ---
    await telegram_bot.stop_polling()
    await telegram_bot.shutdown()

# Create the FastAPI app with the lifespan manager
app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Rolling5 Bot FastAPI server is running."}

@app.get("/status")
def health_check():
    """An endpoint for NeuroSync to check on this service."""
    return {"status": "ok", "service": "Rolling5"}
