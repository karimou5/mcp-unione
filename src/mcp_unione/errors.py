from __future__ import annotations
import json
from functools import lru_cache
from importlib.resources import files


class UniOneError(Exception):
    def __init__(self, code: int | str, message: str, http_status: int | None = None, fix: str | None = None):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.fix = fix
        super().__init__(f"UniOne error {code} (HTTP {http_status}): {message}")

    def as_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message,
                          "http_status": self.http_status, "fix": self.fix}}


@lru_cache(maxsize=1)
def _table() -> dict:
    try:
        return json.loads(files("mcp_unione.data").joinpath("errors.json").read_text("utf-8"))
    except FileNotFoundError:
        return {}


def enrich(code, message: str, http_status: int | None) -> dict:
    info = _table().get(str(code), {})
    return {"code": code, "message": message, "http_status": http_status, "fix": info.get("fix")}
