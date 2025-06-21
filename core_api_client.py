# rolling5/core_api_client.py
import httpx
from config import Config

class CoreApiClient:
    """Handles all API requests to NeuroSync and TradingCore."""
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=15.0)

    async def get_neurosync_status(self):
        """Pings the NeuroSync /status endpoint."""
        try:
            response = await self.client.get(self.config.neurosync_status_url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Error contacting NeuroSync: {e}")
            return {"status": "error", "service": "NeuroSync", "details": str(e)}

    async def get_trading_core_status(self):
        """Pings the TradingCore /status endpoint."""
        try:
            response = await self.client.get(self.config.core_status_url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Error contacting TradingCore: {e}")
            return {"status": "error", "service": "TradingCore", "details": str(e)}

    async def send_command_to_core(self, command: str, user_id: int):
        """Sends a command to the TradingCore."""
        # This is a placeholder for a future endpoint on your TradingCore
        # For now, it just demonstrates the communication path
        url = f"{self.config.core_command_url}/{command}"
        try:
            response = await self.client.post(url, json={"user_id": user_id})
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"status": "error", "details": f"Failed to send command to Core: {e}"}

