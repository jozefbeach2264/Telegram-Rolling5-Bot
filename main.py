import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

# Import all Rolling5 components using absolute imports
from config import config
from core_api_client import CoreApiClient
from command_handler import CommandHandler
from telegram_bot import TelegramBot

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# --- FastAPI Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    logging.info("--- Rolling5 Service Startup ---")
    
    api_client = CoreApiClient(config)
    command_handler = CommandHandler(api_client)
    bot = TelegramBot(config, command_handler)
    
    app.state.bot = bot
    
    asyncio.create_task(bot.start_polling())
    
    yield
    
    logging.info("--- Rolling5 Service Shutdown ---")
    if app.state.bot:
        await app.state.bot.shutdown()
    logging.info("--- Rolling5 Service Shutdown Complete ---")

# --- FastAPI Application ---
app = FastAPI(title="Rolling5 Service API", lifespan=lifespan)

# --- API Endpoints ---
@app.get("/status")
def health_check():
    """A simple health check endpoint for NeuroSync to monitor."""
    return {"status": "ok", "service": "Rolling5"}

@app.post("/alert")
async def receive_alert(request: Request):
    """Endpoint to receive critical alerts from backend services like TradingCore."""
    data = await request.json()
    message = data.get("message")
    level = data.get("level", "INFO")

    if not message:
        return {"status": "error", "detail": "No message provided."}
    
    bot_instance = request.app.state.bot
    if bot_instance:
        logging.info(f"Received alert from backend: '{message}'")
        await bot_instance.send_message_to_user(f"🚨 **Backend Alert ({level})** 🚨\n\n`{message}`")
        return {"status": "ok", "detail": "Alert forwarded."}
    else:
        logging.error("Bot instance not found in app state. Cannot forward alert.")
        return {"status": "error", "detail": "Bot not running."}
