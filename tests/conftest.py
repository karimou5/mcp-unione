import pytest

from mcp_unione.client import UniOneClient
from mcp_unione.config import Settings


@pytest.fixture
def client():
    return UniOneClient(
        Settings(
            api_key="k",
            base_url="https://eu1.unione.io/en/transactional/api/v1",
            timeout=5,
        )
    )


@pytest.fixture
def base():
    return "https://eu1.unione.io/en/transactional/api/v1"
