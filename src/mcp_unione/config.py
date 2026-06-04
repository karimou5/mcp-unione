from __future__ import annotations
import os
from dataclasses import dataclass

_REGIONS = {
    "eu": "https://eu1.unione.io",
    "us": "https://us1.unione.io",
    "global": "https://api.unione.io",
}
_PATH = "/en/transactional/api/v1"

@dataclass(frozen=True)
class Settings:
    api_key: str | None
    base_url: str
    timeout: float

    @classmethod
    def from_env(cls) -> "Settings":
        override = os.getenv("UNIONE_BASE_URL")
        region = (os.getenv("UNIONE_REGION") or "eu").lower()
        host = _REGIONS.get(region, _REGIONS["eu"])
        base_url = override.rstrip("/") if override else host + _PATH
        timeout = float(os.getenv("UNIONE_TIMEOUT") or "30")
        return cls(api_key=os.getenv("UNIONE_API_KEY"), base_url=base_url, timeout=timeout)
