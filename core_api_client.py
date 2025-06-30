import httpx
import logging
from typing import Dict, Any, Optional
from .config import Rolling5Config

logger = logging.getLogger(__name__)

class CoreApiClient:
    """Handles all API requests from the bot to the backend services (NeuroSync and TradingCore)."""
    def __init__(self, config: Rolling5Config):
        self.config = config
        # Use a persistent client for connection pooling and efficiency
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_neurosync_status(self) -> str:
        """Gets the status from the NeuroSync /health endpoint."""
        url = self.config.neuro_health_url
        if not url:
            return "NeuroSync URL not configured."
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json().get("status", "ok")
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to NeuroSync: {e}")
            return "unhealthy"

    async def get_trading_core_status(self) -> str:
        """Gets the status from the TradingCore /status endpoint."""
        url = self.config.core_status_url
        if not url:
            return "TradingCore URL not configured."
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json().get("status", "ok")
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to TradingCore: {e}")
            return "unhealthy"

    async def send_validation_signal(self, strategy: str, user_id: int) -> Dict[str, Any]:
        """Sends a signal to the TradingCore /validate_signal endpoint."""
        url = self.config.core_validate_url
        if not url:
            return {"status": "error", "detail": "CORE_VALIDATE_URL not configured in secrets."}

        # The payload that TradingCore's new AI endpoint will expect
        payload = {
            "strategy": strategy, 
            "user_id": user_id,
            "symbol": "ETHUSDT" # Could be made dynamic
        }
        
        try:
            # This endpoint will now trigger the full AI analysis pipeline
            response = await self.client.post(url, json=payload)
            
            if 200 <= response.status_code < 300:
                return response.json()
            elif response.status_code == 400:
                return {"status": "REJECTED", "decision": {"reasoning": "Signal failed initial validation by TradingCore."}}
            else:
                response.raise_for_status()
                return {"status": "error", "detail": "An unknown error occurred."}
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to TradingCore for validation: {e}")
            return {"status": "error", "detail": f"Failed to connect to TradingCore: {e}"}
