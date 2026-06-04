import importlib
import pytest
from mcp_unione.config import Settings

def test_region_eu_default(monkeypatch):
    monkeypatch.delenv("UNIONE_BASE_URL", raising=False)
    monkeypatch.setenv("UNIONE_REGION", "eu")
    s = Settings.from_env()
    assert s.base_url == "https://eu1.unione.io/en/transactional/api/v1"

def test_region_us(monkeypatch):
    monkeypatch.delenv("UNIONE_BASE_URL", raising=False)
    monkeypatch.setenv("UNIONE_REGION", "us")
    assert Settings.from_env().base_url.startswith("https://us1.unione.io")

def test_base_url_override_wins(monkeypatch):
    monkeypatch.setenv("UNIONE_REGION", "eu")
    monkeypatch.setenv("UNIONE_BASE_URL", "https://x.example/api/v1")
    assert Settings.from_env().base_url == "https://x.example/api/v1"

def test_default_region_when_unset(monkeypatch):
    monkeypatch.delenv("UNIONE_REGION", raising=False)
    monkeypatch.delenv("UNIONE_BASE_URL", raising=False)
    assert "eu1.unione.io" in Settings.from_env().base_url
