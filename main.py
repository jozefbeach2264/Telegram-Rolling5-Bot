# rolling5/main.py
import logging
from fastapi import FastAPI

from config import Config
from core_api_client import CoreApiClient
from command_handler import CommandHandler
from telegram_bot import TelegramBot

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)

# --- FastAPI Application Instance ---
# We define the app object first, then attach events to it.
app = FastAPI()

# --- App State Setup ---
# A dictionary on the app itself to hold our running bot instance
app.state.bot = None

# --- Startup and Shutdown Events ---

@app.on_event("startup")
async def startup_event():
    """
    This function will run when the FastAPI application starts.
    """
    logging.info("Rolling5 service starting up...")
    
    # Initialize all the core components of the bot system
    config = Config()
    api_client = CoreApiClient(config)
    command_handler = CommandHandler(api_client)
    bot = TelegramBot(config, command_handler)
    
    # Store the bot instance in the app state
    app.state.bot = bot
    
    # Initialize and start the bot
    await bot.initialize()
    await bot.start_polling()
    logging.info("Bot has been started and is polling for messages.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    This function will run when the FastAPI application shuts down.
    """
    logging.info("Rolling5 service shutting down...")
    if app.state.bot:
        await app.state.bot.shutdown()
    logging.info("Rolling5 service shut down successfully.")


# --- API Endpoints ---

@app.get("/")
def root():
    """Root endpoint to confirm the service is running."""
    return {"status": "ok", "service": "Rolling5"}
