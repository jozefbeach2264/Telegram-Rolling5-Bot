# rolling5/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

# --- Advanced Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
# Quieten down the noisy Telegram library logs
logging.getLogger("telegram.ext").setLevel(logging.WARNING)
logging.getLogger("telegram.bot").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

from config import Config
from core_api_client import CoreApiClient
from command_handler import CommandHandler
from telegram_bot import TelegramBot

# --- FastAPI Application ---
# We define the app object first, then attach events and routes to it.
app = FastAPI()

# --- App State Setup ---
app.state.bot = None

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events to manage the bot's lifecycle.
    """
    logging.info("Rolling5 service starting up...")
    
    # Initialize components
    config = Config()
    api_client = CoreApiClient(config)
    command_handler = CommandHandler(api_client)
    bot = TelegramBot(config, command_handler)
    
    app.state.bot = bot
    
    # Start the bot
    await bot.initialize()
    await bot.start_polling()
    
    yield
    
    # Shutdown
    logging.info("Rolling5 service shutting down...")
    if app.state.bot:
        await app.state.bot.shutdown()
    logging.info("Rolling5 service shut down successfully.")

# Apply the lifespan manager to the app
app.router.lifespan_context = lifespan

# --- API Endpoints ---

@app.get("/")
def root():
    """Root endpoint to confirm the service is running for web pings."""
    return {"status": "ok", "service": "Rolling5"}

@app.get("/status")
def health_check():
    """A simple health check endpoint for other services to monitor."""
    return {"status": "ok", "service": "Rolling5"}

