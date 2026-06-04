from __future__ import annotations
import httpx
from .config import Settings
from .errors import UniOneError


class UniOneClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def post(self, path: str, payload: dict) -> dict:
        if not self.settings.api_key:
            raise UniOneError(code="no_api_key", message="Missing API key: set UNIONE_API_KEY.", http_status=None)
        url = f"{self.settings.base_url}/{path.lstrip('/')}"
        headers = {"X-API-KEY": self.settings.api_key, "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.settings.timeout) as c:
                resp = await c.post(url, json=payload, headers=headers)
        except httpx.HTTPError as e:
            raise UniOneError(code="transport", message=f"Network error: {e}", http_status=None) from e
        try:
            data = resp.json()
        except ValueError:
            raise UniOneError(code="bad_response", message=resp.text[:300], http_status=resp.status_code)
        if resp.status_code >= 400 or (isinstance(data, dict) and data.get("status") == "error"):
            code = data.get("code", resp.status_code) if isinstance(data, dict) else resp.status_code
            msg = data.get("message", "error") if isinstance(data, dict) else "error"
            from .errors import enrich
            raise UniOneError(code=code, message=msg, http_status=resp.status_code, fix=enrich(code, msg, resp.status_code)["fix"])
        return data
