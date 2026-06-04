import httpx
import pytest
import respx
from mcp_unione.client import UniOneClient
from mcp_unione.config import Settings
from mcp_unione.errors import UniOneError

def _client(key="k"):
    return UniOneClient(Settings(api_key=key, base_url="https://eu1.unione.io/en/transactional/api/v1", timeout=5))

@respx.mock
async def test_post_sends_api_key_and_returns_json():
    route = respx.post("https://eu1.unione.io/en/transactional/api/v1/system/ping.json").mock(
        return_value=httpx.Response(200, json={"status": "success"}))
    out = await _client().post("system/ping.json", {})
    assert out == {"status": "success"}
    assert route.calls.last.request.headers["X-API-KEY"] == "k"

@respx.mock
async def test_error_body_raises_unione_error():
    respx.post(url__regex=r".*/email/send.json").mock(
        return_value=httpx.Response(400, json={"status": "error", "code": 101, "message": "bad key"}))
    with pytest.raises(UniOneError) as ei:
        await _client().post("email/send.json", {})
    assert ei.value.code == 101

async def test_missing_api_key_raises():
    with pytest.raises(UniOneError) as ei:
        await _client(key=None).post("system/info.json", {})
    assert "api key" in str(ei.value).lower()
