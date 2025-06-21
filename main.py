# TelegramBot/main.py (Corrected with Threading)
import uvicorn
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from threading import Thread
import httpx
import asyncio

from config import Config

# --- Bot Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Telegram Bot is online and connected.")

async def check_service_status(url: str, client: httpx.AsyncClient) -> str:
    """Helper function to check the status of a single service."""
    if not url:
        return "Not Configured"
    try:
        response = await client.get(url, timeout=5.0)
        return "✅ ALIVE" if response.status_code == 200 else f"❌ ERROR ({response.status_code})"
    except httpx.RequestError:
        return "❌ UNREACHABLE"

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks the live status of NeuroSync and TradingCore."""
    await update.message.reply_text("Pinging services, please wait...")
    config = Config()
    async with httpx.AsyncClient() as client:
        neuro_status_task = check_service_status(config.neurosync_status_url, client)
        core_status_task = check_service_status(config.core_status_url, client)
        neuro_status, core_status = await asyncio.gather(neuro_status_task, core_status_task)
    reply_text = f"--- System Status ---\n\nNeuroSync:   {neuro_status}\nTradingCore: {core_status}"
    await update.message.reply_text(reply_text)


# --- FastAPI Web Server ---
# This server will run in a background thread to receive notifications
fastapi_app = FastAPI()

@fastapi_app.get("/status")
async def get_bot_status():
    """Health check endpoint for NeuroSync to ping."""
    return {"status": "ok", "service": "TelegramBot"}
    
@fastapi_app.post("/notify")
async def receive_notification(notification: dict):
    # We will implement the logic to forward this to the user later
    print(f"Received notification: {notification}")
    return {"status": "notification received"}

def run_server():
    """Function to run the Uvicorn server."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)


# --- Main Application ---
def main() -> None:
    """Starts the FastAPI server in a thread and then the bot."""
    print("Initializing services...")
    config = Config()

    # Start the FastAPI server in a background thread
    # The 'daemon=True' flag ensures the thread exits when the main program does
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    print("FastAPI server started in a background thread.")
    
    # Setup and run the Telegram Bot in the main thread
    application = Application.builder().token(config.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))

    print("Bot is polling for messages...")
    application.run_polling()


if __name__ == "__main__":
    main()



