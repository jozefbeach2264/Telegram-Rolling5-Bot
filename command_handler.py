# rolling5/command_handler.py
from core_api_client import CoreApiClient

class CommandHandler:
    """Processes user commands and returns responses."""
    def __init__(self, api_client: CoreApiClient):
        self.api_client = api_client

    async def handle_start(self, user_id: int):
        """Handles the /start command."""
        return "Rolling5 Bot is active. Send /status to check system health."

    async def handle_status(self, user_id: int):
        """Handles the /status command by checking all backend services."""
        ns_status = await self.api_client.get_neurosync_status()
        tc_status = await self.api_client.get_trading_core_status()

        ns_icon = "✅" if ns_status.get("status") == "ok" else "❌"
        tc_icon = "✅" if tc_status.get("status") == "ok" else "❌"

        response_text = f"**System Health Status**\n"
        response_text += f"{ns_icon} **NeuroSync:** `{ns_status.get('status', 'error')}`\n"
        response_text += f"{tc_icon} **TradingCore:** `{tc_status.get('status', 'error')}`"
        
        return response_text

    async def handle_unknown(self, user_id: int):
        """Handles any command that isn't recognized."""
        return "Unknown command. Please use /start or /status."

