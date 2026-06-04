from __future__ import annotations

import json
from importlib.resources import files

from mcp.server.fastmcp.resources import FunctionResource


def _manifest() -> list[dict]:
    return json.loads(files("mcp_unione.data").joinpath("manifest.json").read_text("utf-8"))


def _make_reader(slug: str):
    def _read() -> str:
        return files("mcp_unione.data").joinpath("kb", f"{slug}.md").read_text("utf-8")

    return _read


def register(mcp, client=None):
    # One concrete resource per KB page so they enumerate in list_resources().
    for e in _manifest():
        slug, title = e["slug"], e["title"]
        resource = FunctionResource.from_function(
            _make_reader(slug),
            uri=f"unione-docs://{slug}",
            name=title,
            description=e.get("summary", ""),
            mime_type="text/markdown",
        )
        mcp.add_resource(resource)
