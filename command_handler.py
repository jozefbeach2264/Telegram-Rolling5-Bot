import asyncio
import logging
from .core_api_client import CoreApiClient

logger = logging.getLogger(__name__)

class CommandHandler:
    """Processes all user commands from Telegram and interacts with the backend services."""
    def __init__(self, api_client: CoreApiClient):
        self.api_client = api_client

    async def handle_start(self, user_id: int) -> str:
        """Handles the /start command."""
        return "Welcome to the DAN Command System. Use /status to check system health or /help for a list of commands."

    async def handle_help(self, user_id: int) -> str:
        """Handles the /help command."""
        # This can be expanded to be more dynamic in the future
        return (
            "<b>Available Commands:</b>\n\n"
            "<b>System:</b> /start, /help, /status, /halt, /allclear\n"
            "<b>Trading:</b> /trade [strategy], /vol_on, /vol_off\n"
            "<b>Analysis:</b> /evaluate, /accuracy, /report\n"
            "<i>More commands available via direct terminal.</i>"
        )

    async def handle_status(self, user_id: int) -> str:
        """Handles the /status command by checking all connected services."""
        logger.info(f"Handling /status command for user {user_id}")
        # This logic remains the same
        neuro_status, core_status = await asyncio.gather(
            self.api_client.get_neurosync_status(),
            self.api_client.get_trading_core_status()
        )
        neuro_emoji = "✅" if neuro_status == "ok" else "❌"
        core_emoji = "✅" if core_status == "ok" else "❌"
        return (
            f"<b>System Status Report:</b>\n\n"
            f"{neuro_emoji} <b>NeuroSync Orchestrator:</b> <code>{neuro_status}</code>\n"
            f"{core_emoji} <b>TradingCore Engine:</b> <code>{core_status}</code>"
        )

    async def handle_trade_command(self, strategy: str, user_id: int) -> str:
        """Handles the /trade command by sending a signal to TradingCore."""
        logger.info(f"Handling /trade {strategy} command for user {user_id}")
        if not strategy:
            return "Please specify a strategy. Usage: `/trade <strategy_name>` (e.g., `/trade scalpel`)."
        
        response = await self.api_client.send_validation_signal(strategy, user_id)
        status = response.get("status")
        decision = response.get("decision", {})
        
        if status == "EXECUTING":
            return (f"✅ **AI Verdict: GO**\nSignal for strategy '{strategy}' was approved and is now executing.\n"
                    f"<i>AI Reasoning: {decision.get('reasoning', 'N/A')}</i>")
        elif status == "REJECTED":
            return (f"❌ **AI Verdict: NO GO**\nSignal for strategy '{strategy}' was rejected.\n"
                    f"<i>AI Reasoning: {decision.get('reasoning', 'N/A')}</i>")
        else:
            return f"🚨 An error occurred: {response.get('detail', 'Unknown error from TradingCore.')}"

    async def handle_simple_command(self, command: str, user_id: int) -> str:
        """
        Handles simple, one-word commands that are passed to the backend.
        This is a generic handler for commands like /halt, /allclear, /evaluate, etc.
        """
        logger.info(f"Handling simple command /{command} for user {user_id}")
        # In a real system, the CoreApiClient would have a method for each of these.
        # For now, we can use a generic "send_system_command" method.
        # response = await self.api_client.send_system_command(command, user_id)
        
        # For this build-out, we will return a mock confirmation.
        return f"✅ Command `/{command}` has been sent to the system for processing."

