from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Recipient(BaseModel):
    email: str
    substitutions: dict | None = None
    metadata: dict | None = None


class Attachment(BaseModel):
    type: str
    name: str
    content: str  # base64


class Body(BaseModel):
    html: str | None = None
    plaintext: str | None = None
    amp: str | None = None


Engine = Literal["simple", "velocity", "liquid", "none"]
