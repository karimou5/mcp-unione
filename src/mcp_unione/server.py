from mcp.server.fastmcp import FastMCP
from .config import Settings
from .client import UniOneClient
from . import tools, docs_tools, resources, prompts


def build_server() -> FastMCP:
    mcp = FastMCP("unione")
    client = UniOneClient(Settings.from_env())
    tools.register_all(mcp, client)
    docs_tools.register(mcp, client)
    resources.register(mcp)
    prompts.register(mcp)
    return mcp
