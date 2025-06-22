# rolling5/command_handler.py
import asyncio
from core_api_client import CoreApiClient

class CommandHandler:
    """Processes user commands and returns responses."""
    def __init__(self, api_client: CoreApiClient):
        self.api_client = api_client

    async def handle_start(self, user_id: int) -> str:
        """Handles the /start command."""
        return "Welcome to Rolling5! Use /status to check system health or /trade to initiate a signal."

    async def handle_status(self, user_id: int) -> str:
        """Handles the /status command by checking all connected services."""
        neuro_status, core_status = await asyncio.gather(
            self.api_client.get_neurosync_status(),
            self.api_client.get_trading_core_status()
        )

        # Emojis for status
        neuro_emoji = "✅" if neuro_status == "ok" else "❌"
        core_emoji = "✅" if core_status == "ok" else "❌"

        # Format the message
        status_message = (
            f"<b>System Status Report:</b>\n\n"
            f"{neuro_emoji} <b>NeuroSync Engine:</b> <code>{neuro_status}</code>\n"
            f"{core_emoji} <b>TradingCore API:</b> <code>{core_status}</code>"
        )
        return status_message

    async def handle_trade_command(self, strategy: str, user_id: int) -> str:
        """Handles the /trade command by sending a signal to TradingCore."""
        if not strategy:
            return "Please specify a strategy. Usage: `/trade <strategy_name>` (e.g., `/trade trapx`)."

        response = await self.api_client.send_validation_signal(strategy, user_id)

        if response.get("status") == "signal_validated":
            return f"✅ Signal for strategy '{strategy}' was successfully validated by TradingCore!"
        elif response.get("status") == "rejected":
            return f"❌ Signal for strategy '{strategy}' was REJECTED by TradingCore's filters."
        else:
            return f"🚨 An error occurred: {response.get('detail', 'Unknown error.')}"

    async def handle_unknown(self, user_id: int) -> str:
        """Handles any unrecognized commands."""
        return "Sorry, I don't recognize that command. Please try /status or /trade."
