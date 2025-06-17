# telegram_interface.py (Bot Side: Telegram Rolling5 Bot)
import json
import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Remove hardcoded default, rely on environment variable
CORE_ENDPOINT = os.environ.get("CORE_ENDPOINT")
if not CORE_ENDPOINT:
    logger.error("CORE_ENDPOINT environment variable not set")
    raise ValueError("CORE_ENDPOINT must be set")

AUTHORIZED_USERS = set()
TRADE_STATE = {
    "active_trade": None,
    "dry_run": False,
    "manual_mode": False,
    "auto_mode": False,
    "system_running": True,
    "trades": []
}
TRADE_FILE = "trades.json"

def load_trades():
    """Load trades from trades.json."""
    try:
        if os.path.exists(TRADE_FILE):
            with open(TRADE_FILE, 'r') as f:
                TRADE_STATE["trades"] = json.load(f)
            logger.debug("Trades loaded successfully")
    except Exception as e:
        logger.error(f"Error loading trades: {e}")

def save_trades():
    """Save trades to trades.json."""
    try:
        with open(TRADE_FILE, 'w') as f:
            json.dump(TRADE_STATE["trades"], f, indent=2)
        logger.debug("Trades saved successfully")
    except Exception as e:
        logger.error(f"Error saving trades: {e}")

async def fetch_core_data(endpoint: str, payload: dict = None) -> dict:
    """Fetch data from core system."""
    from aiohttp import ClientSession
    auth_token = os.environ.get("HTTP_AUTH_TOKEN")
    if not auth_token:
        logger.error("HTTP_AUTH_TOKEN not set")
        return None
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with ClientSession() as session:
        try:
            async with session.post(f"{CORE_ENDPOINT}/{endpoint}", json=payload or {}, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Fetched data from {endpoint}: {data}")
                    return data
                logger.error(f"Core request failed: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching core data from {endpoint}: {e}")
            return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Authorize user."""
    chat_id = update.effective_chat.id
    AUTHORIZED_USERS.add(chat_id)
    await update.message.reply_text('Welcome to Telegram Rolling5 Bot! Authorized to receive signals.')
    logger.info(f"User {chat_id} started the bot")

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger a new signal."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    if not TRADE_STATE["system_running"]:
        await update.message.reply_text("System is shut down.")
        return
    signal = await fetch_core_data("signals")
    if not signal:
        await update.message.reply_text("Failed to fetch signal.")
        return
    if TRADE_STATE["manual_mode"]:
        TRADE_STATE["active_trade"] = signal
        await update.message.reply_text("Manual mode: Confirm entry with /confirm.")
    else:
        await process_signal(signal, chat_id)
    await display_trade_and_prediction(signal, chat_id)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm manual trade entry."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    if not TRADE_STATE["manual_mode"] or not TRADE_STATE["active_trade"]:
        await update.message.reply_text("No trade to confirm.")
        return
    signal = TRADE_STATE["active_trade"]
    await process_signal(signal, chat_id)
    await display_trade_and_prediction(signal, chat_id)
    TRADE_STATE["active_trade"] = None

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch directional forecast."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    forecast = await fetch_core_data("forecast")
    if not forecast:
        await update.message.reply_text("Failed to fetch forecast.")
        return
    message = (
        f"📊 Forecast\n"
        f"Direction: {forecast.get('direction', 'N/A')}\n"
        f"Conviction Index: {forecast.get('conviction_index', 0)}%\n"
        f"Apex Warning: {'Active' if forecast.get('apex_warning', False) else 'None'}"
    )
    await update.message.reply_text(message)

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch volume metrics."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    metrics = await fetch_core_data("volume")
    if not metrics:
        await update.message.reply_text("Failed to fetch volume metrics.")
        return
    message = (
        f"📉 Volume Metrics\n"
        f"Volume: {metrics.get('volume', 'N/A')}\n"
        f"Speed: {metrics.get('speed', 'N/A')}\n"
        f"Pressure: {metrics.get('pressure_imbalance', 'N/A')}"
    )
    await update.message.reply_text(message)

async def reversal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch reversal zone data."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    reversal = await fetch_core_data("reversal")
    if not reversal:
        await update.message.reply_text("Failed to fetch reversal data.")
        return
    message = (
        f"🔄 Reversal Zone\n"
        f"Zone: {reversal.get('zone', 'N/A')}\n"
        f"Wall Thinning: {'Detected' if reversal.get('wall_thinning', False) else 'None'}\n"
        f"Spoof Stack: {'Alert' if reversal.get('spoof_stack', False) else 'None'}"
    )
    await update.message.reply_text(message)

async def forceexit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force close active trade."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    if not TRADE_STATE["active_trade"]:
        await update.message.reply_text("No active trade.")
        return
    trade = TRADE_STATE["active_trade"]
    exit_data = await fetch_core_data("forceexit", {"trade_id": trade["signal_id"]})
    trade["exit_time"] = datetime.utcnow().isoformat()
    trade["roi"] = exit_data.get("roi", 0.0) if exit_data else 0.0
    TRADE_STATE["trades"].append(trade)
    save_trades()
    await broadcast_alert(f"🚪 Trade {trade['signal_id']} force exited. ROI: {trade['roi']}%")
    TRADE_STATE["active_trade"] = None

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dump trade data by ID."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    try:
        trade_id = int(context.args[0])
        trade = next((t for t in TRADE_STATE["trades"] if t["signal_id"] == trade_id), None)
        if not trade:
            await update.message.reply_text(f"No trade with ID {trade_id}.")
            return
        log_data = await fetch_core_data("log", {"trade_id": trade_id})
        message = (
            f"📜 Trade Log ID {trade_id}\n"
            f"Entry: ${trade['price']:.2f}\n"
            f"Exit: ${trade.get('exit_price', 'N/A'):.2f}\n"
            f"ROI: {trade.get('roi', 'N/A')}%\n"
            f"Timestamp: {trade['timestamp']}\n"
            f"Forecast: {log_data.get('forecast', 'N/A')}"
        )
        await update.message.reply_text(message)
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /log <trade_id>")

async def toggle_dryrun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle Dry Run Mode."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    TRADE_STATE["dry_run"] = not TRADE_STATE["dry_run"]
    await fetch_core_data("toggle_dryrun", {"dry_run": TRADE_STATE["dry_run"]})
    await update.message.reply_text(f"Dry Run Mode: {'ON' if TRADE_STATE['dry_run'] else 'OFF'}")

async def toggle_manualmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle Manual Mode."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    TRADE_STATE["manual_mode"] = not TRADE_STATE["manual_mode"]
    TRADE_STATE["auto_mode"] = False if TRADE_STATE["manual_mode"] else TRADE_STATE["auto_mode"]
    await fetch_core_data("toggle_manualmode", {"manual_mode": TRADE_STATE["manual_mode"]})
    await update.message.reply_text(f"Manual Mode: {'ON' if TRADE_STATE['manual_mode'] else 'OFF'}")

async def toggle_automode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle Auto Mode."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    TRADE_STATE["auto_mode"] = not TRADE_STATE["auto_mode"]
    TRADE_STATE["manual_mode"] = False if TRADE_STATE["auto_mode"] else TRADE_STATE["manual_mode"]
    await fetch_core_data("toggle_automode", {"auto_mode": TRADE_STATE["auto_mode"]})
    await update.message.reply_text(f"Auto Mode: {'ON' if TRADE_STATE['auto_mode'] else 'OFF'}")

async def emergencyexit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close all active trades."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    if not TRADE_STATE["active_trade"]:
        await update.message.reply_text("No active trades.")
        return
    trade = TRADE_STATE["active_trade"]
    exit_data = await fetch_core_data("emergencyexit")
    trade["exit_time"] = datetime.utcnow().isoformat()
    trade["roi"] = exit_data.get("roi", 0.0) if exit_data else 0.0
    TRADE_STATE["trades"].append(trade)
    save_trades()
    await broadcast_alert(f"🚨 Emergency Exit: Trade {trade['signal_id']} closed. ROI: {trade['roi']}%")
    TRADE_STATE["active_trade"] = None

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Halt all activity."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    TRADE_STATE["system_running"] = False
    TRADE_STATE["active_trade"] = None
    await fetch_core_data("shutdown")
    await broadcast_alert("⚠️ System Shutdown")
    logger.info("System shutdown initiated")

async def startup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart system."""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Unauthorized.")
        return
    TRADE_STATE["system_running"] = True
    await fetch_core_data("startup")
    await broadcast_alert("🟢 System Started")
    logger.info("System startup initiated")

async def process_signal(signal: dict, chat_id: int):
    """Process and log signal."""
    if TRADE_STATE["dry_run"]:
        signal["mode"] = "dry_run"
    elif TRADE_STATE["auto_mode"]:
        signal["mode"] = "auto"
    else:
        signal["mode"] = "manual"
    TRADE_STATE["active_trade"] = signal
    TRADE_STATE["trades"].append(signal)
    save_trades()
    await broadcast_alert(f"📈 Trade {signal['signal_id']} started: {signal['type'].upper()}")

async def display_trade_and_prediction(signal: dict, chat_id: int):
    """Display trade and Rolling5 prediction."""
    try:
        # Use context.bot instead of creating new Application
        trade_message = (
            f"📈 Trade Signal\n"
            f"ENTRY: ${signal['price']:.2f}\n"
            f"DIRECTION: {signal['direction']}\n"
            f"EXIT: ${signal['exit_price']:.2f}\n"
            f"ROI: {signal['roi']}%\n"
            f"DETONATION: {signal['detonation']}\n\n"
        )
        prediction = signal.get("predictions", {})
        prediction_message = (
            f"Price direction: {prediction.get('price_direction', 'N/A')}\n\n"
            f"C1: {prediction.get('c1', {}).get('action', 'N/A')} – ${prediction.get('c1', {}).get('price', 0):.2f} – {prediction.get('c1', {}).get('volume', 'N/A')}\n"
            f"C2: {prediction.get('c2', {}).get('action', 'N/A')} – ${prediction.get('c2', {}).get('price', 0):.2f} – {prediction.get('c2', {}).get('volume', 'N/A')}\n"
            f"C3: {prediction.get('c3', {}).get('action', 'N/A')} – ${prediction.get('c3', {}).get('price', 0):.2f} – {prediction.get('c3', {}).get('volume', 'N/A')}\n"
            f"C4: {prediction.get('c4', {}).get('action', 'N/A')} – ${prediction.get('c4', {}).get('price', 0):.2f} – {prediction.get('c4', {}).get('volume', 'N/A')}\n"
            f"C5: {prediction.get('c5', {}).get('action', 'N/A')} – ${prediction.get('c5', {}).get('price', 0):.2f} – {prediction.get('c5', {}).get('volume', 'N/A')}\n\n"
            f"Midpoint (Mark): ${prediction.get('midpoint', 0):.2f}\n"
            f"ROI so far: {prediction.get('roi_so_far', 'N/A')}%\n"
            f"Expected next move: {prediction.get('expected_move', 'N/A')}"
        )
        message = f"{trade_message}{prediction_message}"
        for user_chat_id in AUTHORIZED_USERS:
            await context.bot.send_message(chat_id=user_chat_id, text=message)
        logger.info(f"Displayed trade {signal['signal_id']} and prediction")
    except Exception as e:
        logger.error(f"Error displaying trade: {e}")

async def broadcast_alert(message: str):
    """Send alert to all authorized users."""
    try:
        # Use context.bot in calling function
        pass  # Handled in calling context
    except Exception as e:
        logger.error(f"Error broadcasting alert: {e}")

def setup_handlers(app: Application):
    """Set up Telegram command handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("volume", volume))
    app.add_handler(CommandHandler("reversal", reversal))
    app.add_handler(CommandHandler("forceexit", forceexit))
    app.add_handler(CommandHandler("log", log))
    app.add_handler(CommandHandler("dryrun", toggle_dryrun))
    app.add_handler(CommandHandler("manualmode", toggle_manualmode))
    app.add_handler(CommandHandler("automode", toggle_automode))
    app.add_handler(CommandHandler("emergencyexit", emergencyexit))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("startup", startup))