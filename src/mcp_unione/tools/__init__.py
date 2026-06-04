from . import system  # add domains here as implemented


def register_all(mcp, client) -> None:
    system.register(mcp, client)
    # email.register(mcp, client) ... (added per task)
