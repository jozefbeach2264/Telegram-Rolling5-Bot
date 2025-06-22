import httpx
from config import Config
import logging

logger = logging.getLogger(__name__)

class CoreApiClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0, verify=True)

    async def get_neurosync_status(self):
        url = self.config.neuro_health_url
        logger.debug(f"Requesting NeuroSync status at {url}")
        if not url:
            logger.error("NeuroSync URL not configured.")
            return "NeuroSync URL not configured."
        try:
            response = await self.client.get(url)
            logger.debug(f"NeuroSync response: {response.status_code} {response.text}")
            response.raise_for_status()
            return response.json().get("status", "ok")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} {e.response.text}")
            return "unhealthy"
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return "unhealthy"

    async def get_trading_core_status(self):
        url = self.config.core_status_url
        logger.debug(f"Requesting TradingCore status at {url}")
        if not url:
            logger.error("TradingCore URL not configured.")
            return "TradingCore URL not configured."
        try:
            response = await self.client.get(url)
            logger.debug(f"TradingCore response: {response.status_code} {response.text}")
            response.raise_for_status()
            return response.json().get("status", "ok")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} {e.response.text}")
            return "unhealthy"
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return "unhealthy"

    async def send_validation_signal(self, strategy: str, user_id: int) -> dict:
        url = self.config.core_validate_url
        logger.debug(f"Sending signal to {url}")
        if not url:
            logger.error("CORE_VALIDATE_URL not configured.")
            return {"status": "error", "detail": "CORE_VALIDATE_URL not configured."}
        payload = {"strategy": strategy, "user_id": user_id}
        try:
            response = await self.client.post(url, json=payload)
            logger.debug(f"Validation response: {response.status_code} {response.text}")
            if 200 <= response.status_code < 300:
                return response.json()
            elif response.status_code == 400:
                return {"status": "rejected", "detail": "Signal failed validation."}
            else:
                logger.error(f"Unexpected status: {response.status_code} {response.text}")
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} {e.response.text}")
            return {"status": "error", "detail": f"HTTP error: {e}"}
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {"status": "error", "detail": f"Request error: {e}"}